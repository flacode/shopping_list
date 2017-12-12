from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
import jwt
from app import app, db

class Users(db.Model):
    """Class for user attributes and methods"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(500))

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = generate_password_hash(password)

    def save(self):
        """Save new users and changes to the database"""
        db.session.add(self)
        db.session.commit()

    def delete(self):
        """Delete user from the database"""
        db.session.delete(self)
        db.session.commit()

    def generate_token(self, user_id):
        """Generate token for authentication and return string"""
        try:
            # set up payload with expiration date
            payload = {
                'exp': datetime.utcnow() + timedelta(minutes=60),
                'iat': datetime.utcnow(),
                'sub': user_id
            }
            return jwt.encode(
                payload,
                app.config.get('SECRET_KEY'),
                algorithm='HS256'
            )
        except Exception as e:
            return str(e)

    @staticmethod
    def decode_token(token):
        """Decodes token from the authorization header"""
        try:
            # try to decode the token using the secret variable
            payload = jwt.decode(token, app.config.get('SECRET_KEY'))
            is_blacklisted_token = BlacklistTokens.check_blacklist(token)
            if is_blacklisted_token:
                return 'You are logged out. Please log in again.'
            else:
                return payload['sub']
        except jwt.ExpiredSignatureError:
            # token has expired, return n error string
            return "Expired token. Please login to get new token"
        except jwt.InvalidTokenError:
            return "Invalid token. Please register or login"


    def __repr__(self):
        return '<User %r>' % self.username


class ShoppingLists(db.Model):
    """Class with methods for a shopping list"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    due_date = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship('Users',
                           backref=db.backref('shopping_lists', cascade="all,delete", lazy='dynamic'))

    def __init__(self, name, user_id, due_date=None):
        self.name = name
        self.due_date = due_date
        self.user_id = user_id

    def __repr__(self):
        return '<Shopping List: %r>' % self.name

    def save(self):
        """Save new users and changes to the database"""
        db.session.add(self)
        db.session.commit()

    def delete(self):
        """Delete shopping list from the database"""
        db.session.delete(self)
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
                                    backref=db.backref('items', cascade="all,delete", lazy='dynamic'))

    def __init__(self, name, quantity, shopping_list_id, bought_from=None, status=None):
        self.name = name
        self.quantity = quantity
        self.shopping_list_id = shopping_list_id
        self.bought_from = bought_from
        self.status = status

    def __repr__(self):
        return '<Item %r>' % self.name

    def save(self):
        """Save new users and changes to the database"""
        db.session.add(self)
        db.session.commit()

    def delete(self):
        """Delete item from the database"""
        db.session.delete(self)
        db.session.commit()


class BlacklistTokens(db.Model):
    """Class for storing blacklisted tokens"""
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    token = db.Column(db.String(500), unique=True, nullable=False)
    blacklisted_on = db.Column(db.DateTime, nullable=False)

    def __init__(self, token):
        self.token = token
        self.blacklisted_on = datetime.utcnow()

    def save(self):
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def check_blacklist(token):
        # check whether token has been blacklisted
        res = BlacklistTokens.query.filter_by(token=str(token)).first()
        if res:
            return True
        else:
            return False

    def __repr__(self):
        return '<id: token: {}'.format(self.token)