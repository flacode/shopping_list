import os
import json
import unittest
import tempfile
from run import app, db
from models import Users

class UsersTestCase(unittest.TestCase):
    """Testcases for the Users class"""
    def setUp(self):
        self.db_fd, app.config['DATABASE'] = tempfile.mkstemp()
        app.testing = True
        self.app = app.test_client()
        self.user = {"username": "flacode", "password": "flavia", "email": "fnshem@gmail.com"}
        with app.app_context():
            db.create_all()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(app.config['DATABASE'])

    def test_user_account_creation(self):
        result = self.app.post('/auth/register', data=self.user, follow_redirects=True)
        print(result)
        print(result.status_code)
        self.assertEqual(result.status_code, 201)

    def test_user_login(self):
        user = Users(username=self.user['username'], email=self.user['email'], password=self.user['password'])
        result = self.app.post('/auth/login', data=dict(username="flacode", password="flavia"), follow_redirects=True)
        assert b'User logged in successfully' in result.data

