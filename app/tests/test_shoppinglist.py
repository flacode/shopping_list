import os
import json
import unittest
import tempfile
from base64 import b64encode
from app import app, db


class ShoppingListTestCase(unittest.TestCase):
    """Testcases for the ShoppingLists class"""
    def setUp(self):
        self.db_fd, app.config['DATABASE'] = tempfile.mkstemp()
        app.testing = True
        self.app = app.test_client()
        self.user = {"username": "flacode", "password": "flavia", "email": "fnshem@gmail.com"}
        self.shopping_list = {"name": "bakery", "due_date": "2017-08-17"}
        self.shopping_list1 = {"name": "food", "due_date": "2017-08-18"}
        self.shopping_list2 = {"name": "hardware", "due_date": "2017-08-19"}
        self.shopping_list_error = {"name": "food store"}
        with app.app_context():
            db.drop_all()
            db.create_all()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(app.config['DATABASE'])

    def login_user(self):
        user_pass = b64encode(b"flacode:flavia").decode("ascii")
        headers = {'Authorization': 'Basic %s' % user_pass}
        return self.app.post('/auth/login', headers=headers)

    def test_create_shopping_list_for_authenticated_user(self):
        """Test create shopping list for user"""
        self.app.post('/auth/register', data=json.dumps(self.user),
                      headers={'Content-Type': 'application/json'})
        res = self.login_user()
        # obtain access token
        access_token = json.loads(res.data.decode())['access_token']
        result = self.app.post('/shoppinglists/',
                               data=json.dumps(self.shopping_list),
                               headers={'Content-Type': 'application/json',
                                        'Authorization': access_token})
        self.assertEqual(result.status_code, 201)
        self.assertIn('Shopping list created.', str(result.data))
        res_error = self.app.post('/shoppinglists/',
                                  data=json.dumps(self.shopping_list_error),
                                  headers={'Content-Type': 'application/json',
                                           'Authorization': access_token})
        self.assertEqual(res_error.status_code, 400)
        self.assertIn('Missing attributes, shopping list not created.', str(res_error.data))

    def test_create_shopping_list_for_unauthenticated_user(self):
        """Test create shopping list for unregisterd user"""
        result = self.app.post('/shoppinglists/', data=json.dumps(self.shopping_list),
                               headers={'Content-Type': 'application/json'})
        self.assertEqual(result.status_code, 401)
        self.assertIn('Please register  or login.', str(result.data))

    def test_view_all_shopping_lists(self):
        """Test to view all shopping lists"""
        self.app.post('/auth/register', data=json.dumps(self.user),
                      headers={'Content-Type': 'application/json'})
        res = self.login_user()
        # obtain access token
        access_token = json.loads(res.data.decode())['access_token']
        result = self.app.get('/shoppinglists/',
                              headers={'Authorization': access_token})
        self.assertEqual(result.status_code, 200)
        self.assertIn('No shopping lists created yet.', str(result.data))
        self.app.post('/shoppinglists/', data=json.dumps(self.shopping_list),
                      headers={'Content-Type': 'application/json',
                               'Authorization': access_token})
        shopping_lists = self.app.get('/shoppinglists/',
                                      headers={'Authorization': access_token})
        self.assertIn('shopping_lists', str(shopping_lists.data))

    def test_view_all_shopping_lists_with_query(self):
        """Test to view all shopping lists with a query string in url"""
        self.app.post('/auth/register', data=json.dumps(self.user),
                      headers={'Content-Type': 'application/json'})
        res = self.login_user()
        # obtain access token
        access_token = json.loads(res.data.decode())['access_token']
        self.app.post('/shoppinglists/', data=json.dumps(self.shopping_list),
                      headers={'Content-Type': 'application/json',
                               'Authorization': access_token})
        shopping_lists = self.app.get('/shoppinglists/',
                                      headers={'Authorization': access_token})
        self.assertIn('shopping_lists', str(shopping_lists.data))
        shopping_list = self.app.get('/shoppinglists/?q=bakery',
                                     headers={'Authorization': access_token})
        self.assertIn('shopping_lists', str(shopping_list.data))
        result = self.app.get('/shoppinglists/?q=abc',
                              headers={'Authorization': access_token})
        self.assertEqual(result.status_code, 200)
        self.assertIn('Shopping list to match the search key not found.',
                      str(result.data))

    def test_view_all_shopping_lists_with_limit(self):
        """Test to view all shopping lists with a limit on the number of posts per page"""
        self.app.post('/auth/register', data=json.dumps(self.user),
                      headers={'Content-Type': 'application/json'})
        res = self.login_user()
        # obtain access token
        access_token = json.loads(res.data.decode())['access_token']
        self.app.post('/shoppinglists/', data=json.dumps(self.shopping_list),
                      headers={'Content-Type': 'application/json',
                               'Authorization': access_token})
        self.app.post('/shoppinglists/', data=json.dumps(self.shopping_list1),
                      headers={'Content-Type': 'application/json',
                               'Authorization': access_token})
        self.app.post('/shoppinglists/', data=json.dumps(self.shopping_list2),
                      headers={'Content-Type': 'application/json',
                               'Authorization': access_token})
        shopping_lists = self.app.get('/shoppinglists/',
                                      headers={'Authorization': access_token})
        self.assertIn('shopping_lists', str(shopping_lists.data))
        self.assertIn('hardware', str(shopping_lists.data))
        shopping_list = self.app.get('/shoppinglists/?limit=2&page=1',
                                     headers={'Authorization': access_token})
        self.assertIn('bakery', str(shopping_list.data))
        self.assertIn('food', str(shopping_list.data))
        self.assertNotIn('hardware', str(shopping_list.data))

    def test_view_all_shopping_lists_unauthenticated_user(self):
        result = self.app.get('/shoppinglists/')
        self.assertEqual(result.status_code, 401)
        self.assertIn('Please register  or login.', str(result.data))
              
    def test_view_one_shopping_list(self):
        """Test if user can view saved shopping list"""
        self.app.post('/auth/register', data=json.dumps(self.user),
                      headers={'Content-Type': 'application/json'})
        res = self.login_user()
        # obtain access token
        access_token = json.loads(res.data.decode())['access_token']
        # if shopping list is not saved in the database
        result = self.app.get('/shoppinglists/1', headers={'Authorization': access_token})
        self.assertEqual(result.status_code, 404)
        self.assertIn('Shopping list can not be found', str(result.data))
        self.app.post('/shoppinglists/', data=json.dumps(self.shopping_list),
                      headers={'Content-Type': 'application/json', 'Authorization': access_token})
        shopping_list = self.app.get('/shoppinglists/1', headers={'Authorization': access_token})
        self.assertEqual(shopping_list.status_code, 200)
        self.assertIn('shopping list', str(shopping_list.data))

    def test_update_shopping_list(self):
        """Test if user can update shopping list details"""
        self.app.post('/auth/register', data=json.dumps(self.user),
                      headers={'Content-Type': 'application/json'})
        res = self.login_user()
        # obtain access token
        access_token = json.loads(res.data.decode())['access_token']
        # if shopping list is not saved in the database
        result = self.app.put('/shoppinglists/1', data=json.dumps({"name": "new_name"}),
                              headers={'Content-Type': 'application/json', 'Authorization': access_token})
        self.assertEqual(result.status_code, 404)
        self.assertIn('Shopping list can not be found', str(result.data))
        self.app.post('/shoppinglists/', data=json.dumps(self.shopping_list),
                      headers={'Content-Type': 'application/json', 'Authorization': access_token})
        update_shopping_list = self.app.put('/shoppinglists/1', data=json.dumps({"name": "new_name"}),
                                            headers={'Content-Type': 'application/json', 'Authorization': access_token})
        self.assertEqual(update_shopping_list.status_code, 200)
        self.assertIn('Shopping list has been updated', str(update_shopping_list.data))

    def test_delete_shopping_list(self):
        """Test to delete shopping list from the database"""
        self.app.post('/auth/register', data=json.dumps(self.user),
                      headers={'Content-Type': 'application/json'})
        res = self.login_user()
        # obtain access token
        access_token = json.loads(res.data.decode())['access_token']
        result = self.app.delete('/shoppinglists/1', headers={'Authorization': access_token})
        self.assertEqual(result.status_code, 404)
        self.assertIn('Shopping list can not be found', str(result.data))
        self.app.post('/shoppinglists/', data=json.dumps(self.shopping_list),
                      headers={'Content-Type': 'application/json', 'Authorization': access_token})
        deleted = self.app.delete('/shoppinglists/1', headers={'Authorization': access_token})
        self.assertEqual(deleted.status_code, 200)
        self.assertIn('Shopping list successfully deleted', str(deleted.data))