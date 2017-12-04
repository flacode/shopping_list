import os
import json
import unittest
import tempfile
from base64 import b64encode
from app import app, db, url_prefix


class ShoppingListTestCase(unittest.TestCase):
    """Testcases for the ShoppingLists class"""
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
        self.shopping_list1 = {
            "name": "food",
            "due_date": "2017-08-18"
            }
        self.shopping_list2 = {
            "name": "hardware",
            "due_date": "2017-08-19"
            }
        self.shopping_list_error = {"name": "food store"}
        with app.app_context():
            db.drop_all()
            db.create_all()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(app.config['DATABASE'])

    def login_user(self):
        return self.app.post(url_prefix+'/auth/login',
                             data=json.dumps({
                                 "username": "flacode",
                                 "password": "flavia"
                                 }),
                             headers={'Content-Type': 'application/json'})

    def test_create_shopping_list_for_authenticated_user(self):
        """Test create shopping list for user"""
        self.app.post(url_prefix+'/auth/register',
                      data=json.dumps(self.user),
                      headers={'Content-Type': 'application/json'})
        res = self.login_user()
        # obtain access token
        access_token = json.loads(res.data.decode())['access_token']
        result = self.app.post(url_prefix+'/shoppinglists/',
                               data=json.dumps(self.shopping_list),
                               headers={'Content-Type': 'application/json',
                                        'Authorization': access_token})
        self.assertEqual(result.status_code, 201)
        self.assertIn('Shopping list created.', str(result.data))
        res_error = self.app.post(url_prefix+'/shoppinglists/',
                                  data=json.dumps(self.shopping_list_error),
                                  headers={'Content-Type': 'application/json',
                                           'Authorization': access_token})
        self.assertEqual(res_error.status_code, 400)
        self.assertIn('Missing attributes, shopping list not created.',
                      str(res_error.data))

    def test_create_shopping_list_for_unauthenticated_user(self):
        """Test create shopping list for unregistered user"""
        result = self.app.post(url_prefix+'/shoppinglists/',
                               data=json.dumps(self.shopping_list),
                               headers={'Content-Type': 'application/json'})
        self.assertEqual(result.status_code, 401)
        self.assertIn('Please register or login.', str(result.data))
        res = self.app.post(url_prefix+'/shoppinglists/',
                            data=json.dumps(self.shopping_list),
                            headers={'Content-Type': 'application/json',
                                     'Authorization': 'adnckddee'})
        self.assertEqual(res.status_code, 401)
        self.assertIn('Invalid token. Please register or login', str(res.data))

    def test_view_all_shopping_lists(self):
        """Test to view all shopping lists"""
        no_token = self.app.get(url_prefix+'/shoppinglists/')
        self.assertEqual(no_token.status_code, 401)
        self.assertIn('Please register or login.', str(no_token.data))
        self.app.post(url_prefix+'/auth/register', data=json.dumps(self.user),
                      headers={'Content-Type': 'application/json'})
        res = self.login_user()
        # obtain access token
        access_token = json.loads(res.data.decode())['access_token']
        result = self.app.get(url_prefix+'/shoppinglists/',
                              headers={'Authorization': access_token})
        self.assertEqual(result.status_code, 200)
        self.assertIn('No shopping lists created yet.', str(result.data))
        self.app.post(url_prefix+'/shoppinglists/',
                      data=json.dumps(self.shopping_list),
                      headers={'Content-Type': 'application/json',
                               'Authorization': access_token})
        shopping_lists = self.app.get(url_prefix+'/shoppinglists/',
                                      headers={'Authorization': access_token})
        self.assertIn('shopping_lists', str(shopping_lists.data))

    def test_view_all_shopping_lists_with_query(self):
        """Test to view all shopping lists with a query string in url"""
        self.app.post(url_prefix+'/auth/register', data=json.dumps(self.user),
                      headers={'Content-Type': 'application/json'})
        res = self.login_user()
        # obtain access token
        access_token = json.loads(res.data.decode())['access_token']
        self.app.post(url_prefix+'/shoppinglists/',
                      data=json.dumps(self.shopping_list),
                      headers={'Content-Type': 'application/json',
                               'Authorization': access_token})
        shopping_lists = self.app.get(url_prefix+'/shoppinglists/',
                                      headers={'Authorization': access_token})
        self.assertIn('shopping_lists', str(shopping_lists.data))
        shopping_list = self.app.get(url_prefix+'/shoppinglists/?q=bakery',
                                     headers={'Authorization': access_token})
        self.assertIn('shopping_lists', str(shopping_list.data))
        result = self.app.get(url_prefix+'/shoppinglists/?q=abc',
                              headers={'Authorization': access_token})
        self.assertEqual(result.status_code, 200)
        self.assertIn('Shopping list to match the search key not found.',
                      str(result.data))

    def test_view_all_shopping_lists_with_limit(self):
        """Test to view all shopping lists with a limit on
           the number of posts per page
        """
        self.app.post(url_prefix+'/auth/register', data=json.dumps(self.user),
                      headers={'Content-Type': 'application/json'})
        res = self.login_user()
        # obtain access token
        access_token = json.loads(res.data.decode())['access_token']
        self.app.post(url_prefix+'/shoppinglists/',
                      data=json.dumps(self.shopping_list),
                      headers={'Content-Type': 'application/json',
                               'Authorization': access_token})
        self.app.post(url_prefix+'/shoppinglists/',
                      data=json.dumps(self.shopping_list1),
                      headers={'Content-Type': 'application/json',
                               'Authorization': access_token})
        self.app.post(url_prefix+'/shoppinglists/',
                      data=json.dumps(self.shopping_list2),
                      headers={'Content-Type': 'application/json',
                               'Authorization': access_token})
        shopping_lists = self.app.get(url_prefix+'/shoppinglists/',
                                      headers={'Authorization': access_token})
        self.assertIn('shopping_lists', str(shopping_lists.data))
        self.assertIn('hardware', str(shopping_lists.data))
        shopping_list = self.app.get(
            url_prefix+'/shoppinglists/?limit=2&page=1',
            headers={'Authorization': access_token}
            )
        self.assertIn('bakery', str(shopping_list.data))
        self.assertIn('food', str(shopping_list.data))
        self.assertNotIn('hardware', str(shopping_list.data))

    def test_view_all_shopping_lists_unauthenticated_user(self):
        result = self.app.get(url_prefix+'/shoppinglists/')
        self.assertEqual(result.status_code, 401)
        self.assertIn('Please register or login.', str(result.data))

    def test_view_one_shopping_list(self):
        """Test if user can view saved shopping list"""
        no_token = self.app.get(url_prefix+'/shoppinglists/1')
        self.assertEqual(no_token.status_code, 401)
        self.assertIn('Please register or login.', str(no_token.data))
        forged_token = self.app.get(url_prefix+'/shoppinglists/1',
                                    headers={'Authorization': 'abcdefgh'})
        self.assertEqual(forged_token.status_code, 401)
        self.assertIn('Invalid token. Please register or login',
                      str(forged_token.data))
        self.app.post(url_prefix+'/auth/register', data=json.dumps(self.user),
                      headers={'Content-Type': 'application/json'})
        res = self.login_user()
        # obtain access token
        access_token = json.loads(res.data.decode())['access_token']
        # if shopping list is not saved in the database
        result = self.app.get(url_prefix+'/shoppinglists/1',
                              headers={'Authorization': access_token})
        self.assertEqual(result.status_code, 404)
        self.assertIn('Shopping list can not be found', str(result.data))
        self.app.post(url_prefix+'/shoppinglists/',
                      data=json.dumps(self.shopping_list),
                      headers={
                          'Content-Type': 'application/json',
                          'Authorization': access_token
                          })
        shopping_list = self.app.get(url_prefix+'/shoppinglists/1',
                                     headers={'Authorization': access_token})
        self.assertEqual(shopping_list.status_code, 200)
        self.assertIn('shopping list', str(shopping_list.data))

    def test_update_shopping_list(self):
        """Test if user can update shopping list details"""
        no_token = self.app.put(url_prefix+'/shoppinglists/1',
                                data=json.dumps({"name": "new_name"}),
                                headers={'Content-Type': 'application/json'})
        self.assertEqual(no_token.status_code, 401)
        self.assertIn('Please register or login.', str(no_token.data))
        forged_token = self.app.put(url_prefix+'/shoppinglists/1',
                                    data=json.dumps({"name": "new_name"}),
                                    headers={
                                        'Content-Type': 'application/json',
                                        'Authorization': 'acsksskks'})
        self.assertEqual(forged_token.status_code, 401)
        self.assertIn('Invalid token. Please register or login',
                      str(forged_token.data))
        self.app.post(url_prefix+'/auth/register',
                      data=json.dumps(self.user),
                      headers={'Content-Type': 'application/json'})
        res = self.login_user()
        # obtain access token
        access_token = json.loads(res.data.decode())['access_token']
        # if shopping list is not saved in the database
        result = self.app.put(url_prefix+'/shoppinglists/1',
                              data=json.dumps({"name": "new_name"}),
                              headers={
                                  'Content-Type': 'application/json',
                                  'Authorization': access_token})
        self.assertEqual(result.status_code, 404)
        self.assertIn('Shopping list can not be found', str(result.data))
        self.app.post(url_prefix+'/shoppinglists/',
                      data=json.dumps(self.shopping_list),
                      headers={
                          'Content-Type': 'application/json',
                          'Authorization': access_token
                          })
        update_shopping_list = self.app.put(
            url_prefix+'/shoppinglists/1',
            data=json.dumps({"name": "new_name", "due_date": "2017-09-18"}),
            headers={
                'Content-Type': 'application/json',
                'Authorization': access_token
                })
        self.assertEqual(update_shopping_list.status_code, 200)
        self.assertIn('Shopping list has been updated',
                      str(update_shopping_list.data))

    def test_delete_shopping_list(self):
        """Test to delete shopping list from the database"""
        no_token = self.app.delete(url_prefix+'/shoppinglists/1',
                                   data=json.dumps({"name": "new_name"}),
                                   headers={
                                       'Content-Type': 'application/json'
                                       })
        self.assertEqual(no_token.status_code, 401)
        self.assertIn('Please register or login.', str(no_token.data))
        forged_token = self.app.delete(url_prefix+'/shoppinglists/1',
                                       data=json.dumps({"name": "new_name"}),
                                       headers={
                                           'Content-Type': 'application/json',
                                           'Authorization': 'acsksskks'
                                           })
        self.assertEqual(forged_token.status_code, 401)
        self.assertIn('Invalid token. Please register or login',
                      str(forged_token.data))
        self.app.post(url_prefix+'/auth/register',
                      data=json.dumps(self.user),
                      headers={'Content-Type': 'application/json'})
        res = self.login_user()
        # obtain access token
        access_token = json.loads(res.data.decode())['access_token']
        result = self.app.delete(url_prefix+'/shoppinglists/1',
                                 headers={'Authorization': access_token})
        self.assertEqual(result.status_code, 404)
        self.assertIn('Shopping list can not be found', str(result.data))
        self.app.post(url_prefix+'/shoppinglists/',
                      data=json.dumps(self.shopping_list),
                      headers={
                          'Content-Type': 'application/json',
                          'Authorization': access_token
                          })
        deleted = self.app.delete(url_prefix+'/shoppinglists/1',
                                  headers={'Authorization': access_token})
        self.assertEqual(deleted.status_code, 200)
        self.assertIn('Shopping list successfully deleted', str(deleted.data))
