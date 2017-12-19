"""Tests for the ShoppingLists model"""
import json
from app import url_prefix
from .test_setup import BaseTestCase


class ShoppingListTestCase(BaseTestCase):
    """Testcases for the ShoppingLists class"""
    def setUp(self):
        super(ShoppingListTestCase, self).setUp()
        self.shopping_list1 = {
            "name": "food",
            "due_date": "2017-08-18"
            }
        self.shopping_list2 = {
            "name": "hardware",
            "due_date": "2017-08-19"
            }
        self.shopping_list_error = {"name": "food store"}

    def login_user(self):
        """Method to login user"""
        res = self.app.post(url_prefix+'/auth/login',
                            data=json.dumps({
                                "username": "flacode",
                                "password": "flavia"
                                }),
                            headers={'Content-Type': 'application/json'})
        return json.loads(res.data.decode())['access_token']

    def test_create_for_authenticated_user(self):
        """Test create shopping list for user"""
        self.app.post(url_prefix+'/auth/register',
                      data=json.dumps(self.user),
                      headers={'Content-Type': 'application/json'})
        # obtain access token
        access_token = self.login_user()
        result = self.app.post(url_prefix+'/shoppinglists/',
                               data=json.dumps(self.shopping_list),
                               headers={'Content-Type': 'application/json',
                                        'Authorization': access_token})
        self.assertEqual(result.status_code, 201)
        self.assertIn('Shopping list created.', str(result.data))

    def test_create_with_authenticated_user_missing_attributes(self):
        """
            Test create shopping list for authenticated user with missing
            attributes.
        """
        self.app.post(url_prefix+'/auth/register',
                      data=json.dumps(self.user),
                      headers={'Content-Type': 'application/json'})
        # obtain access token
        access_token = self.login_user()
        res_error = self.app.post(url_prefix+'/shoppinglists/',
                                  data=json.dumps(self.shopping_list_error),
                                  headers={'Content-Type': 'application/json',
                                           'Authorization': access_token})
        self.assertEqual(res_error.status_code, 400)
        self.assertIn('Missing attributes, shopping list not created.',
                      str(res_error.data))

    def test_create_without_access_token(self):
        """Test create shopping list for user without an access token"""
        result = self.app.post(url_prefix+'/shoppinglists/',
                               data=json.dumps(self.shopping_list),
                               headers={'Content-Type': 'application/json'})
        self.assertEqual(result.status_code, 401)
        self.assertIn('Please register or login.', str(result.data))

    def test_create_with_invalid_access_token(self):
        """Test create shopping list for user without an access token"""
        res = self.app.post(url_prefix+'/shoppinglists/',
                            data=json.dumps(self.shopping_list),
                            headers={'Content-Type': 'application/json',
                                     'Authorization': 'adnckddee'})
        self.assertEqual(res.status_code, 401)
        self.assertIn('Invalid token. Please register or login', str(res.data))

    def test_view_all_without_access_token(self):
        """Test to view all shopping lists without access token"""
        no_token = self.app.get(url_prefix+'/shoppinglists/')
        self.assertEqual(no_token.status_code, 401)
        self.assertIn('Please register or login.', str(no_token.data))

    def test_view_all_authenticated_user_without_shoppinglists(self):
        """
            Test view shopping lists without any shopping lists
            created yet.
        """
        self.app.post(url_prefix+'/auth/register',
                      data=json.dumps(self.user),
                      headers={'Content-Type': 'application/json'})
        # obtain access token
        access_token = self.login_user()
        result = self.app.get(url_prefix+'/shoppinglists/',
                              headers={'Authorization': access_token})
        self.assertEqual(result.status_code, 200)
        self.assertIn('No shopping lists created yet.', str(result.data))

    def test_view_all_authenticated_user_with_shoppinglists(self):
        """
            View all shopping lists for authenticated user with shopping
        """
        self.app.post(url_prefix+'/auth/register',
                      data=json.dumps(self.user),
                      headers={'Content-Type': 'application/json'})
        # obtain access token
        access_token = self.login_user()
        self.app.post(url_prefix+'/shoppinglists/',
                      data=json.dumps(self.shopping_list),
                      headers={'Content-Type': 'application/json',
                               'Authorization': access_token})
        shopping_lists = self.app.get(url_prefix+'/shoppinglists/',
                                      headers={'Authorization': access_token})
        self.assertIn('shopping_lists', str(shopping_lists.data))

    def test_view_all_with_query(self):
        """Test to view all shopping lists with a query string in url"""
        self.app.post(url_prefix+'/auth/register', data=json.dumps(self.user),
                      headers={'Content-Type': 'application/json'})
        # obtain access token
        access_token = self.login_user()
        self.app.post(url_prefix+'/shoppinglists/',
                      data=json.dumps(self.shopping_list),
                      headers={'Content-Type': 'application/json',
                               'Authorization': access_token})
        shopping_list = self.app.get(url_prefix+'/shoppinglists/?q=bakery',
                                     headers={'Authorization': access_token})
        self.assertIn('shopping_lists', str(shopping_list.data))

    def test_view_all_with_non_existent_key(self):
        """
            Test to view all shopping lists with a key that is not included in
            the created shopping list.
        """
        self.app.post(url_prefix+'/auth/register', data=json.dumps(self.user),
                      headers={'Content-Type': 'application/json'})
        # obtain access token
        access_token = self.login_user()
        self.app.post(url_prefix+'/shoppinglists/',
                      data=json.dumps(self.shopping_list),
                      headers={'Content-Type': 'application/json',
                               'Authorization': access_token})
        result = self.app.get(url_prefix+'/shoppinglists/?q=abc',
                              headers={'Authorization': access_token})
        self.assertEqual(result.status_code, 200)
        self.assertIn('Shopping list to match the search key not found.',
                      str(result.data))

    def test_view_all_with_limit(self):
        """Test to view all shopping lists with a limit on
           the number of posts per page
        """
        self.app.post(url_prefix+'/auth/register', data=json.dumps(self.user),
                      headers={'Content-Type': 'application/json'})
        # obtain access token
        access_token = self.login_user()
        # create several shopping lists for pagination
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
        shopping_list = self.app.get(
            url_prefix+'/shoppinglists/?limit=2&page=1',
            headers={'Authorization': access_token}
            )
        self.assertIn('bakery', str(shopping_list.data))
        self.assertIn('food', str(shopping_list.data))
        self.assertNotIn('hardware', str(shopping_list.data))

    def test_view_all_with_limit_no_page(self):
        """Test to view all shopping lists with a limit on
           the number of posts per page but page number is
           greater than number of available pages.
        """
        self.app.post(url_prefix+'/auth/register', data=json.dumps(self.user),
                      headers={'Content-Type': 'application/json'})
        # obtain access token
        access_token = self.login_user()
        # create several shopping lists for pagination
        self.app.post(url_prefix+'/shoppinglists/',
                      data=json.dumps(self.shopping_list),
                      headers={'Content-Type': 'application/json',
                               'Authorization': access_token})
        shopping_list = self.app.get(
            url_prefix+'/shoppinglists/?limit=1&page=10',
            headers={'Authorization': access_token}
            )
        self.assertIn('There are no shopping lists on this page.',
                      str(shopping_list.data))

    def test_view_one_without_access_token(self):
        """Test if user can view saved shopping list without token"""
        no_token = self.app.get(url_prefix+'/shoppinglists/1')
        self.assertEqual(no_token.status_code, 401)
        self.assertIn('Please register or login.', str(no_token.data))

    def test_view_one_with_invalid_access_token(self):
        """Test if user can view saved shopping list without invalid token"""
        forged_token = self.app.get(url_prefix+'/shoppinglists/1',
                                    headers={'Authorization': 'abcdefgh'})
        self.assertEqual(forged_token.status_code, 401)
        self.assertIn('Invalid token. Please register or login',
                      str(forged_token.data))

    def test_view_one_with_valid_access_token_but_empty(self):
        """
            Test view one shopping list with valid access token
            but shopping list is not created.
        """
        self.app.post(url_prefix+'/auth/register', data=json.dumps(self.user),
                      headers={'Content-Type': 'application/json'})
        # obtain access token
        access_token = self.login_user()
        # if shopping list is not saved in the database
        result = self.app.get(url_prefix+'/shoppinglists/1',
                              headers={'Authorization': access_token})
        self.assertEqual(result.status_code, 404)
        self.assertIn('Shopping list can not be found', str(result.data))

    def test_view_one_with_valid_access_token(self):
        """
            Test view one shopping list with valid access token
            but shopping list is created.
        """
        self.app.post(url_prefix+'/auth/register', data=json.dumps(self.user),
                      headers={'Content-Type': 'application/json'})
        # obtain access token
        access_token = self.login_user()
        # create shopping list
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

    def test_update_without_access_token(self):
        """
            Test if user can update shopping list details
            without access token
        """
        no_token = self.app.put(url_prefix+'/shoppinglists/1',
                                data=json.dumps({"name": "new_name"}),
                                headers={'Content-Type': 'application/json'})
        self.assertEqual(no_token.status_code, 401)
        self.assertIn('Please register or login.', str(no_token.data))

    def test_update_with_invalid_access_token(self):
        """
            Test if user can update shopping list details
            with invalid access token
        """
        forged_token = self.app.put(url_prefix+'/shoppinglists/1',
                                    data=json.dumps({"name": "new_name"}),
                                    headers={
                                        'Content-Type': 'application/json',
                                        'Authorization': 'acsksskks'})
        self.assertEqual(forged_token.status_code, 401)
        self.assertIn('Invalid token. Please register or login',
                      str(forged_token.data))

    def test_update_non_existent_shopping_list_with_valid_access_token(self):
        """
            Test if user can update shopping list details with
            valid access token for non existing shopping list
        """
        self.app.post(url_prefix+'/auth/register',
                      data=json.dumps(self.user),
                      headers={'Content-Type': 'application/json'})
        # obtain access token
        access_token = self.login_user()
        # if shopping list is not saved in the database
        result = self.app.put(url_prefix+'/shoppinglists/1',
                              data=json.dumps({"name": "new_name"}),
                              headers={
                                  'Content-Type': 'application/json',
                                  'Authorization': access_token})
        self.assertEqual(result.status_code, 404)
        self.assertIn('Shopping list can not be found', str(result.data))

    def test_update_existing_shopping_list_with_valid_access_token(self):
        """
            Test if user can update shopping list details valid access token
            and shopping list has been created.
        """
        self.app.post(url_prefix+'/auth/register',
                      data=json.dumps(self.user),
                      headers={'Content-Type': 'application/json'})
        # obtain access token
        access_token = self.login_user()
        # create shopping list
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

    def test_delete_shopping_list_without_access_token(self):
        """Test to delete shopping list from the database"""
        no_token = self.app.delete(url_prefix+'/shoppinglists/1',
                                   data=json.dumps({"name": "new_name"}),
                                   headers={
                                       'Content-Type': 'application/json'
                                       })
        self.assertEqual(no_token.status_code, 401)
        self.assertIn('Please register or login.', str(no_token.data))

    def test_delete_shopping_list_with_invalid_token(self):
        """Test delete shopping list with an invalid token"""
        forged_token = self.app.delete(url_prefix+'/shoppinglists/1',
                                       data=json.dumps({"name": "new_name"}),
                                       headers={
                                           'Content-Type': 'application/json',
                                           'Authorization': 'acsksskks'
                                           })
        self.assertEqual(forged_token.status_code, 401)
        self.assertIn('Invalid token. Please register or login',
                      str(forged_token.data))

    def test_delete_non_existent_shopping_list(self):
        """
            Test delete with autheticated user but
            non existing shopping list
            """
        self.app.post(url_prefix+'/auth/register',
                      data=json.dumps(self.user),
                      headers={'Content-Type': 'application/json'})
        # obtain access token
        access_token = self.login_user()
        result = self.app.delete(url_prefix+'/shoppinglists/1',
                                 headers={'Authorization': access_token})
        self.assertEqual(result.status_code, 404)
        self.assertIn('Shopping list can not be found', str(result.data))

    def test_delete_with_existing_shopping_list(self):
        """Test delete with authenticated user and existing shopping list"""
        self.app.post(url_prefix+'/auth/register',
                      data=json.dumps(self.user),
                      headers={'Content-Type': 'application/json'})
        # obtain access token
        access_token = self.login_user()
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
