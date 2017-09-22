import os
import json
import unittest
import tempfile
from base64 import b64encode
from run import app, db


class UsersTestCase(unittest.TestCase):
    """Testcases for the Users class"""
    def setUp(self):
        self.db_fd, app.config['DATABASE'] = tempfile.mkstemp()
        app.testing = True
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
        result = self.app.post('/auth/register', data=json.dumps(self.user),
                               headers={'Content-Type': 'application/json'})
        self.assertEqual(result.status_code, 201)

    def test_user_account_creation_with_existing_account(self):
        """Test user account creation with an exixting username"""
        self.app.post('/auth/register', data=json.dumps(self.user),
                      headers={'Content-Type': 'application/json'})
        result = self.app.post('/auth/register', data=json.dumps(self.user),
                               headers={'Content-Type': 'application/json'})
        self.assertEqual(result.status_code, 202)

    def test_user_login_with_correct_password(self):
        """Test user login with correct credentials"""
        self.app.post('/auth/register', data=json.dumps(self.user),
                      headers={'Content-Type': 'application/json'})
        user_pass = b64encode(b"flacode:flavia").decode("ascii")
        headers = {'Authorization': 'Basic %s' % user_pass}
        result = self.app.post('/auth/login', headers=headers)
        result_data = json.loads(result.data.decode())
        self.assertEqual(result.status_code, 200)
        self.assertIn('User logged in successfully', str(result.data))
        self.assertTrue(result_data['access_token'])

    def test_user_login_with_incorrect_password(self):
        """Test user login with incorrect password"""
        self.app.post('/auth/register', data=json.dumps(self.user),
                      headers={'Content-Type': 'application/json'})
        user_pass = b64encode(b"flacode:123").decode("ascii")
        headers = {'Authorization': 'Basic %s' % user_pass}
        result = self.app.post('/auth/login', headers=headers)
        self.assertEqual(result.status_code, 401)
        self.assertIn('Invalid user credentials', str(result.data))

    def test_user_login_with_non_existing_account(self):
        """Test user login with a username that is not registered"""
        self.app.post('/auth/register', data=json.dumps(self.user),
                      headers={'Content-Type': 'application/json'})
        user_pass = b64encode(b"odette:123").decode("ascii")
        headers = {'Authorization': 'Basic %s' % user_pass}
        result = self.app.post('/auth/login', headers=headers)
        self.assertEqual(result.status_code, 401)
        self.assertIn('User does not exist', str(result.data))

    def test_reset_password(self):
        """Test user reset password"""
        self.app.post('/auth/register', data=json.dumps(self.user),
                      headers={'Content-Type': 'application/json'})
        reset = self.app.post('/auth/reset-password',
                              data=json.dumps({"username": "flacode",
                                              "password": "new_password"}),
                              headers={'Content-Type': 'application/json'})
        self.assertEqual(reset.status_code, 200)
        self.assertIn('You have successfully changed your password.', str(reset.data))
        user_pass = b64encode(b"flacode:new_password").decode("ascii")
        headers = {'Authorization': 'Basic %s' % user_pass}
        result = self.app.post('/auth/login', headers=headers)
        self.assertEqual(result.status_code, 200)

    def test_reset_password_with_non_existent_user(self):
        """Test user reset password"""
        self.app.post('/auth/register', data=json.dumps(self.user),
                      headers={'Content-Type': 'application/json'})
        reset = self.app.post('/auth/reset-password',
                              data=json.dumps({"username": "sammy",
                                              "password": "new_password"}),
                              headers={'Content-Type': 'application/json'})
        self.assertEqual(reset.status_code, 404)
        self.assertIn('No user information found', str(reset.data))
