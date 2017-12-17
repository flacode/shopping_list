import os
import unittest
from app import app
from app.models import db


class BaseTestCase(unittest.TestCase):
    """Set up requirements for all tests"""
    def setUp(self):
        postgres = {
            'user': 'postgres',
            'pw': '',
            'db': 'shoppinglisttdb',
            'host': 'localhost',
            'port': '5432',
        }
        db_uri = 'postgresql://%(user)s:%(pw)s@%(host)s:%(port)s/%(db)s' % postgres
        app.config['TESTING'] = True
        if os.environ.get('DATABASE_URL'):
            app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
        else:
            app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
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
        with app.app_context():
            db.create_all()

    def tearDown(self):
        with app.app_context():
            db.drop_all()
