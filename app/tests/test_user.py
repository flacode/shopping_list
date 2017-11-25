import os
import json
import unittest
import tempfile
from app import app, url_prefix
from app.models import db


class UsersTestCase(unittest.TestCase):
    """Testcases for the Users class"""
    def setUp(self):
        self.db_fd, app.config['DATABASE'] = tempfile.mkstemp()
        app.config['TESTING'] = True
        self.app = app.test_client()
        self.user = {"username": "flacode", "password": "flavia", "email": "fnshem@gmail.com"}
        with app.app_context():
            db.drop_all()
            db.create_all()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(app.config['DATABASE'])

    def test_user_account_creation(self):
        """Test user login"""
        result = self.app.post(url_prefix+'/auth/register', data=json.dumps(self.user),
                               headers={'Content-Type': 'application/json'})
        self.assertEqual(result.status_code, 201)

    def test_user_account_creation_with_incorrect_fields(self):
        """Test user registration with mispelt username"""
        result = self.app.post(url_prefix+'/auth/register',
                               data=json.dumps({"useame": "flacode", "password": "flavia", "email": "fnshem@gmail.com"}),
                               headers={'Content-Type': 'application/json'})
        self.assertEqual(result.status_code, 401)

    def test_user_account_creation_with_missing_fields(self):
        """Test user registration with missing fields"""
        result = self.app.post(url_prefix+'/auth/register',
                               data=json.dumps({"username": "flacode", "password": "flavia"}),
                               headers={'Content-Type': 'application/json'})
        self.assertEqual(result.status_code, 401)

    def test_user_account_creation_with_existing_account(self):
        """Test user account creation with an exixting username"""
        self.app.post(url_prefix+'/auth/register', data=json.dumps(self.user),
                      headers={'Content-Type': 'application/json'})
        result = self.app.post(url_prefix+'/auth/register', data=json.dumps(self.user),
                               headers={'Content-Type': 'application/json'})
        self.assertEqual(result.status_code, 202)

    def test_user_login_with_username(self):
        """Test user login with correct credentials"""
        self.app.post(url_prefix+'/auth/register', data=json.dumps(self.user),
                      headers={'Content-Type': 'application/json'})
        result = self.app.post(url_prefix+'/auth/login',
                               data=json.dumps({"username": "flacode", "password": "flavia"}),
                               headers={'Content-Type': 'application/json'})
        result_data = json.loads(result.data.decode())
        self.assertEqual(result.status_code, 200)
        self.assertIn('User logged in successfully', str(result.data))
        self.assertTrue(result_data['access_token'])

    def test_user_login_with_email(self):
        """Test user login with correct credentials"""
        self.app.post(url_prefix+'/auth/register', data=json.dumps(self.user),
                      headers={'Content-Type': 'application/json'})
        result = self.app.post(url_prefix+'/auth/login',
                               data=json.dumps({"email": "fnshem@gmail.com", "password": "flavia"}),
                               headers={'Content-Type': 'application/json'})
        result_data = json.loads(result.data.decode())
        self.assertEqual(result.status_code, 200)
        self.assertIn('User logged in successfully', str(result.data))
        self.assertTrue(result_data['access_token'])

    def test_user_login_with_incorrect_password(self):
        """Test user login with incorrect password"""
        self.app.post(url_prefix+'/auth/register', data=json.dumps(self.user),
                      headers={'Content-Type': 'application/json'})
        result = self.app.post(url_prefix+'/auth/login',
                               data=json.dumps({"username": "flacode", "password": "fvia"}),
                               headers={'Content-Type': 'application/json'})
        self.assertEqual(result.status_code, 401)
        self.assertIn('Invalid user credentials', str(result.data))

    def test_user_login_with_non_existing_account(self):
        """Test user login with a username that is not registered"""
        self.app.post(url_prefix+'/auth/register', data=json.dumps(self.user),
                      headers={'Content-Type': 'application/json'})
        result = self.app.post(url_prefix+'/auth/login',
                               data=json.dumps({"username": "oddy", "password": "fvia"}),
                               headers={'Content-Type': 'application/json'})
        self.assertEqual(result.status_code, 401)
        self.assertIn('User account does not exist', str(result.data))

    def test_user_login_with_incorrect_fields(self):
        """Test user login with incorrect fields supplied"""
        self.app.post(url_prefix+'/auth/register', data=json.dumps(self.user),
                      headers={'Content-Type': 'application/json'})
        result = self.app.post(url_prefix+'/auth/login',
                               data=json.dumps({"usme": "flacode", "password": "fvia"}),
                               headers={'Content-Type': 'application/json'})
        self.assertEqual(result.status_code, 401)
        self.assertIn('Fields required for login not supplied', str(result.data))

    def test_user_login_with_missing_fields(self):
        """Test user login with missing fields"""
        self.app.post(url_prefix+'/auth/register', data=json.dumps(self.user),
                      headers={'Content-Type': 'application/json'})
        result = self.app.post(url_prefix+'/auth/login',
                               data=json.dumps({"username": "flacode"}),
                               headers={'Content-Type': 'application/json'})
        self.assertEqual(result.status_code, 401)
        self.assertIn('Fields required for login not supplied', str(result.data))

    def test_reset_password_with_username(self):
        """Test user reset password"""
        self.app.post(url_prefix+'/auth/register', data=json.dumps(self.user),
                      headers={'Content-Type': 'application/json'})
        reset = self.app.post(url_prefix+'/auth/reset-password',
                              data=json.dumps({"username": "flacode",
                                               "password": "new_password"}),
                              headers={'Content-Type': 'application/json'})
        self.assertEqual(reset.status_code, 200)
        self.assertIn('You have successfully changed your password.', str(reset.data))
        result = self.app.post(url_prefix+'/auth/login',
                               data=json.dumps({"username": "flacode", "password": "new_password"}),
                               headers={'Content-Type': 'application/json'})
        self.assertEqual(result.status_code, 200)
    
    def test_reset_password_with_email(self):
        """Test user reset password"""
        self.app.post(url_prefix+'/auth/register', data=json.dumps(self.user),
                      headers={'Content-Type': 'application/json'})
        reset = self.app.post(url_prefix+'/auth/reset-password',
                              data=json.dumps({"email": "fnshem@gmail.com",
                                              "password": "new_password"}),
                              headers={'Content-Type': 'application/json'})
        self.assertEqual(reset.status_code, 200)
        self.assertIn('You have successfully changed your password.', str(reset.data))
        result = self.app.post(url_prefix+'/auth/login',
                               data=json.dumps({"username": "flacode", "password": "new_password"}),
                               headers={'Content-Type': 'application/json'})
        self.assertEqual(result.status_code, 200)

    def test_rest_password_with_mispelt_fields(self):
        """Test reset password with mispelt fields"""
        self.app.post(url_prefix+'/auth/register', data=json.dumps(self.user),
                      headers={'Content-Type': 'application/json'})
        reset = self.app.post(url_prefix+'/auth/reset-password',
                              data=json.dumps({"email": "fnshem@gmail.com",
                                              "pswd": "new_password"}),
                              headers={'Content-Type': 'application/json'})
        self.assertEqual(reset.status_code, 401)
        self.assertIn('Fields required for reset password not supplied', str(reset.data))

    def test_user_reset_password_with_missing_fields(self):
        """Test reset password with some fields missing"""
        self.app.post(url_prefix+'/auth/register', data=json.dumps(self.user),
                      headers={'Content-Type': 'application/json'})
        reset = self.app.post(url_prefix+'/auth/reset-password',
                              data=json.dumps({"email": "fnshem@gmail.com",}),
                              headers={'Content-Type': 'application/json'})
        self.assertEqual(reset.status_code, 401)
        self.assertIn('Fields required for reset password not supplied', str(reset.data))

    def test_reset_password_with_non_existent_user(self):
        """Test user reset password"""
        self.app.post(url_prefix+'/auth/register', data=json.dumps(self.user),
                      headers={'Content-Type': 'application/json'})
        reset = self.app.post(url_prefix+'/auth/reset-password',
                              data=json.dumps({"username": "sammy",
                                              "password": "new_password"}),
                              headers={'Content-Type': 'application/json'})
        self.assertEqual(reset.status_code, 404)
        self.assertIn('No user information found', str(reset.data))

    def test_user_logout(self):
        """test user logout"""
        self.app.post(url_prefix+'/auth/register', data=json.dumps(self.user),
                      headers={'Content-Type': 'application/json'})
        res = self.app.post(url_prefix+'/auth/login',
                            data=json.dumps({"email": "fnshem@gmail.com", "password": "flavia"}),
                            headers={'Content-Type': 'application/json'})
        access_token = json.loads(res.data.decode())['access_token']
        result = self.app.post(url_prefix+'/auth/logout',
                               headers={'Content-Type': 'application/json',
                                        'Authorization': access_token})
        self.assertEqual(result.status_code, 200)
        self.assertIn('Successfully logged out', str(result.data))
        logout = self.app.post(url_prefix+'/auth/logout',
                               headers={'Content-Type': 'application/json',
                                        'Authorization': access_token})
        self.assertEqual(logout.status_code, 401)
        self.assertIn('You are logged out. Please log in again.', str(logout.data))

    
    def test_user_with_invalid_token(self):
        """test user logout with invalid token"""
        result = self.app.post(url_prefix+'/auth/logout',
                               headers={'Content-Type': 'application/json',
                                        'Authorization': "abcdefghijklm"})
        self.assertEqual(result.status_code, 401)
        self.assertIn('Invalid token. Please register or login', str(result.data))
        no_token = self.app.post(url_prefix+'/auth/logout',
                                 headers={'Content-Type': 'application/json'})
        self.assertEqual(no_token.status_code, 401)
        self.assertIn('Please register or login', str(no_token.data))

    def test_get_all_users(self):
        """Test view all users in database"""
        result = self.app.get(url_prefix+'/auth/users')
        self.assertEqual(result.status_code, 200)
        self.assertIn('No users registered yet', str(result.data))
        self.app.post(url_prefix+'/auth/register', data=json.dumps(self.user),
                            headers={'Content-Type': 'application/json'})
        result = self.app.get(url_prefix+'/auth/users')
        self.assertEqual(result.status_code, 200)
        self.assertIn('Users', str(result.data))

    def test_get_one_user(self):
        """Test get one user account"""
        self.app.post(url_prefix+'/auth/register', data=json.dumps(self.user),
                      headers={'Content-Type': 'application/json'})
        result = self.app.get(url_prefix+'/auth/user/1')
        self.assertEqual(result.status_code, 200)
        self.assertIn('user', str(result.data))
        no_user = result = self.app.get(url_prefix+'/auth/user/3')
        self.assertEqual(no_user.status_code, 404)
        self.assertIn('User account not found', str(no_user.data))

    def test_delete_user(self):
        """Test delete user account"""
        result = self.app.delete(url_prefix+'/auth/user/1')
        self.assertEqual(result.status_code, 404)
        self.assertIn('User account not found', str(result.data))
        self.app.post(url_prefix+'/auth/register', data=json.dumps(self.user),
                      headers={'Content-Type': 'application/json'})
        del_user = self.app.delete(url_prefix+'/auth/user/1')
        self.assertEqual(del_user.status_code, 200)
        self.assertIn('User account successfully deleted', str(del_user.data))









