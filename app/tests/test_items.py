import os
import json
import unittest
import tempfile
from base64 import b64encode
from app import app, url_prefix
from app.models import db


class ItemsTestCase(unittest.TestCase):
    """Testcases for the Items class"""
    def setUp(self):
        self.db_fd, app.config['DATABASE'] = tempfile.mkstemp()
        app.testing = True
        self.app = app.test_client()
        self.user = {
            "username": "flacode",
            "password": "flavia",
            "email": "fnshem@gmail.com"
            }
        self.shopping_list = {
            "name": "bakery",
            "due_date": "2017-08-17"
            }
        self.item = {
            "name": "sweetpotatoes",
            "quantity": 6,
            "bought_from": "kalerwe",
            "status": "false"
            }
        with app.app_context():
            db.drop_all()
            db.create_all()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(app.config['DATABASE'])

    def login_user(self):
        res = self.app.post(url_prefix+'/auth/login',
                            data=json.dumps({
                                "username": "flacode",
                                "password": "flavia"
                                }),
                            headers={'Content-Type': 'application/json'})
        return json.loads(res.data.decode())['access_token']

    def test_add_item_with_no_access_token(self):
        """Test to add items to a shopping list without access token"""
        no_token = self.app.post(url_prefix+'/shoppinglists/1/items/',
                                 data=json.dumps(self.item),
                                 headers={'Content-Type': 'application/json'})
        self.assertEqual(no_token.status_code, 401)
        self.assertIn('Please register or login.', str(no_token.data))

    def test_add_item_with_invalid_access_token(self):
        """Test to add items to a shopping list with invalid access token"""
        forged_token = self.app.post(url_prefix+'/shoppinglists/1/items/',
                                     data=json.dumps(self.item),
                                     headers={
                                         'Content-Type': 'application/json',
                                         'Authorization': 'abcdkff'
                                         })
        self.assertEqual(forged_token.status_code, 401)
        self.assertIn('Invalid token. Please register or login',
                      str(forged_token.data))

    def test_add_item_with_valid_access_token_no_shopping_list(self):
        """
            Test add item for authenticated user with non
            existent shopping list
        """
        self.app.post(url_prefix+'/auth/register', data=json.dumps(self.user),
                      headers={'Content-Type': 'application/json'})
        # obtain access token
        access_token = self.login_user()
        result = self.app.post(url_prefix+'/shoppinglists/1/items/',
                               data=json.dumps(self.item),
                               headers={
                                   'Content-Type': 'application/json',
                                   'Authorization': access_token
                                   })
        self.assertEqual(result.status_code, 404)
        self.assertIn('Shopping list can not be found to add items',
                      str(result.data))

    def test_add_item_with_valid_access_token_with_shopping_list(self):
        """
            Test add item for authenticated user with an
            existent shopping list
        """
        self.app.post(url_prefix+'/auth/register', data=json.dumps(self.user),
                      headers={'Content-Type': 'application/json'})
        # obtain access token
        access_token = self.login_user()
        # create shopping list and add items to shopping list
        self.app.post(url_prefix+'/shoppinglists/',
                      data=json.dumps(self.shopping_list),
                      headers={
                          'Content-Type': 'application/json',
                          'Authorization': access_token
                          })
        item = self.app.post(url_prefix+'/shoppinglists/1/items/',
                             data=json.dumps(self.item),
                             headers={
                                 'Content-Type': 'application/json',
                                 'Authorization': access_token
                                 })
        self.assertEqual(item.status_code, 201)
        self.assertIn('Item added to shopping list', str(item.data))

    def test_update_item_without_access_token(self):
        """Test update item in shopping list without access token"""
        no_token = self.app.put(url_prefix+'/shoppinglists/1/items/1',
                                data=json.dumps({"name": "new_name"}),
                                headers={'Content-Type': 'application/json'})
        self.assertEqual(no_token.status_code, 401)
        self.assertIn('Please register or login.', str(no_token.data))

    def test_update_item_with_invalid_access_token(self):
        """Test update item in shopping list with invalid access token"""
        forged_token = self.app.put(url_prefix+'/shoppinglists/1/items/1',
                                    data=json.dumps({"name": "new_name"}),
                                    headers={
                                        'Content-Type': 'application/json',
                                        'Authorization': 'kfjkffkjj'
                                        })
        self.assertEqual(forged_token.status_code, 401)
        self.assertIn('Invalid token. Please register or login',
                      str(forged_token.data)
                      )
    def test_update_item_without_shopping_list(self):
        """
            Test update item in shopping list for authenticated user but
            shopping list does not exist
        """
        self.app.post(url_prefix+'/auth/register', data=json.dumps(self.user),
                      headers={'Content-Type': 'application/json'})
        # obtain access token
        access_token = self.login_user()
        # if shopping list is not saved in the database
        result = self.app.put(url_prefix+'/shoppinglists/1/items/1',
                              data=json.dumps({"name": "new_name"}),
                              headers={'Content-Type': 'application/json',
                                       'Authorization': access_token})
        self.assertEqual(result.status_code, 404)
        self.assertIn('Shopping list can not be found to update items',
                      str(result.data))

    def test_update_item_with_shopping_list_without_item(self):
        """
            Test update item in shopping list for authenticated user and
            existing shopping list but does not contain item to update.
        """
        self.app.post(url_prefix+'/auth/register', data=json.dumps(self.user),
                      headers={'Content-Type': 'application/json'})
        # obtain access token
        access_token = self.login_user()
        # create shopping list
        self.app.post(url_prefix+'/shoppinglists/',
                      data=json.dumps(self.shopping_list),
                      headers={'Content-Type': 'application/json',
                               'Authorization': access_token})
        # update item that is not in the shopping list
        item = self.app.put(url_prefix+'/shoppinglists/1/items/1',
                            data=json.dumps({"name": "new_name"}),
                            headers={'Content-Type': 'application/json',
                                     'Authorization': access_token})
        self.assertEqual(item.status_code, 404)
        self.assertIn('Item can not be found in shopping list', str(item.data))

    def test_update_item_with_shopping_list_with_item(self):
        """
            Test update item in shopping list for authenticated user and
            existing shopping list and contains item to update.
        """
        self.app.post(url_prefix+'/auth/register', data=json.dumps(self.user),
                      headers={'Content-Type': 'application/json'})
        # obtain access token
        access_token = self.login_user()
        # create shopping list
        self.app.post(url_prefix+'/shoppinglists/',
                      data=json.dumps(self.shopping_list),
                      headers={'Content-Type': 'application/json',
                               'Authorization': access_token})
        # add item to shopping list
        self.app.post(url_prefix+'/shoppinglists/1/items/',
                      data=json.dumps(self.item),
                      headers={'Content-Type': 'application/json',
                               'Authorization': access_token}
                      )
        # update item in shopping list
        update_item = self.app.put(url_prefix+'/shoppinglists/1/items/1',
                                   data=json.dumps({"name": "new_name"}),
                                   headers={'Content-Type': 'application/json',
                                            'Authorization': access_token}
                                   )
        self.assertEqual(update_item.status_code, 200)
        self.assertIn('Item updated', str(update_item.data))

    def test_view_items_without_token(self):
        """View items in a shopping list without access token"""
        no_token = self.app.get(url_prefix+'/shoppinglists/1/items/')
        self.assertEqual(no_token.status_code, 401)
        self.assertIn('Please register or login.', str(no_token.data))

    def test_view_items_with_invalid_token(self):
        """View items in a shopping list with invalid access token"""
        forged_token = self.app.get(url_prefix+'/shoppinglists/1/items/',
                                    headers={'Authorization': 'abdjdlk'})
        self.assertEqual(forged_token.status_code, 401)
        self.assertIn('Invalid token. Please register or login',
                      str(forged_token.data))

    def test_view_items_without_shopping_list(self):
        """
            View items in a shopping list with access token
            but without shopping list
        """
        # create user
        self.app.post(url_prefix+'/auth/register', data=json.dumps(self.user),
                      headers={'Content-Type': 'application/json'})
        # obtain access token
        access_token = self.login_user()
        shopping_list = self.app.get(url_prefix+'/shoppinglists/1/items/',
                                     headers={'Authorization': access_token})
        self.assertEqual(shopping_list.status_code, 404)
        self.assertIn('Shopping list can not be found',
                      str(shopping_list.data))

    def test_view_items_with_empty_shopping_list(self):
        """
            View items in a shopping list with access token
            but empty shopping list.
        """
         # create user
        self.app.post(url_prefix+'/auth/register', data=json.dumps(self.user),
                      headers={'Content-Type': 'application/json'})
        # obtain access token
        access_token = self.login_user()
        # create shopping list
        self.app.post(url_prefix+'/shoppinglists/',
                      data=json.dumps(self.shopping_list),
                      headers={'Content-Type': 'application/json',
                               'Authorization': access_token})
        shopping_list = self.app.get(url_prefix+'/shoppinglists/1/items/',
                                     headers={'Authorization': access_token})
        self.assertEqual(shopping_list.status_code, 200)
        self.assertIn('Shopping list is empty', str(shopping_list.data))

    def test_view_items_in_shopping_list(self):
        """
            View items in a shopping list with access token
            and shopping list with some items.
        """
         # create user
        self.app.post(url_prefix+'/auth/register', data=json.dumps(self.user),
                      headers={'Content-Type': 'application/json'})
        # obtain access token
        access_token = self.login_user()
        # create shopping list
        self.app.post(url_prefix+'/shoppinglists/',
                      data=json.dumps(self.shopping_list),
                      headers={'Content-Type': 'application/json',
                               'Authorization': access_token})
        # add item
        self.app.post(url_prefix+'/shoppinglists/1/items/',
                      data=json.dumps(self.item),
                      headers={'Content-Type': 'application/json',
                               'Authorization': access_token}
                      )
        shopping_list = self.app.get(url_prefix+'/shoppinglists/1/items/',
                                     headers={'Authorization': access_token})
        self.assertEqual(shopping_list.status_code, 200)
        self.assertIn('Items', str(shopping_list.data))

    def test_delete_item_without_token(self):
        """
            Test delete item from shopping list given its id
            but without providing an access token.
        """
        no_token = self.app.delete(url_prefix+'/shoppinglists/1/items/1')
        self.assertEqual(no_token.status_code, 401)
        self.assertIn('Please register or login.', str(no_token.data))

    def test_delete_item_with_invalid_token(self):
        """
            Test delete item from shopping list given its id 
            but providing an  invalid access token.
        """
        forged_token = self.app.delete(url_prefix+'/shoppinglists/1/items/1',
                                       headers={'Authorization': 'hddhhd'}
                                       )
        self.assertEqual(forged_token.status_code, 401)
        self.assertIn('Invalid token. Please register or login',
                      str(forged_token.data))

    def test_delete_item_without_shopping_list(self):
        """
            Test delete item from shopping list given its id 
            for authenticated user without a shopping list.
        """
        self.app.post(url_prefix+'/auth/register', data=json.dumps(self.user),
                      headers={'Content-Type': 'application/json'})
        # obtain access token
        access_token = self.login_user()
        deleted = self.app.delete(url_prefix+'/shoppinglists/1/items/1',
                                  headers={'Authorization': access_token})
        self.assertEqual(deleted.status_code, 404)
        self.assertIn('Shopping list can not be found to update items',
                      str(deleted.data))

    def test_delete_non_existing_item(self):
        """
            Test delete item from shopping list given its id 
            for authenticated user with an empty shopping list
        """
        self.app.post(url_prefix+'/auth/register', data=json.dumps(self.user),
                      headers={'Content-Type': 'application/json'})
        # obtain access token
        access_token = self.login_user()
        # create shopping list
        self.app.post(url_prefix+'/shoppinglists/',
                      data=json.dumps(self.shopping_list),
                      headers={'Content-Type': 'application/json',
                               'Authorization': access_token})
        deleted = self.app.delete(url_prefix+'/shoppinglists/1/items/1',
                                  headers={'Authorization': access_token})
        self.assertEqual(deleted.status_code, 404)
        self.assertIn('Item can not be found in shopping list',
                      str(deleted.data)
                      )

    def test_delete_existing_item(self):
        """
            Test delete item from shopping list given its id 
            for authenticated user.
        """
        self.app.post(url_prefix+'/auth/register', data=json.dumps(self.user),
                      headers={'Content-Type': 'application/json'})
        # obtain access token
        access_token = self.login_user()
        # create shopping list
        self.app.post(url_prefix+'/shoppinglists/',
                      data=json.dumps(self.shopping_list),
                      headers={'Content-Type': 'application/json',
                               'Authorization': access_token})
        # create item
        self.app.post(url_prefix+'/shoppinglists/1/items/',
                      data=json.dumps(self.item),
                      headers={'Content-Type': 'application/json',
                               'Authorization': access_token})
        deleted = self.app.delete(url_prefix+'/shoppinglists/1/items/1',
                                  headers={'Authorization': access_token}
                                  )
        self.assertEqual(deleted.status_code, 200)
        self.assertIn('Item successfully deleted from shopping list',
                      str(deleted.data))
