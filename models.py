from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from app import app

db = SQLAlchemy(app)


class Users(db.Model):
    """Class for user attributes and methods"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80))
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(20))

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = Bcrypt().generate_password_hash(password).decode()

    def save(self):
        """Save new users and changes to the database"""
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def get_all():
        return Users.query.all()

    def __repr__(self):
        return '<User %r>' % self.username


class ShoppingLists(db.Model):
    """Class with methods for a shopping list"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    due_date = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship('Users',
                           backref=db.backref('shopping_lists', lazy='dynamic'))

    def __init__(self, name, user, due_date=None):
        self.name = name
        self.due_date = due_date
        self.user = user

    def __repr__(self):
        return '<Shopping List: %r>' % self.name

    def save(self):
        """Save new users and changes to the database"""
        db.session.add(self)
        db.session.commit()


class Items(db.Model):
    """Class for the Items in a shopping list"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    quantity = db.Column(db.Integer)
    bought_from = db.Column(db.String(120))
    status = db.Column(db.Boolean)
    shopping_list_id = db.Column(db.Integer, db.ForeignKey('shopping_lists.id'))
    shopping_list = db.relationship('ShoppingLists',
                                    backref=db.backref('items', lazy='dynamic'))

    def __init__(self, name, quantity, shopping_list, bought_from=None, status=None):
        self.name = name
        self.quantity = quantity
        self.shopping_list = shopping_list
        self.bought_from = bought_from
        self.status = status

    def __repr__(self):
        return '<Item %r>' % self.name

    def save(self):
        """Save new users and changes to the database"""
        db.session.add(self)
        db.session.commit()
