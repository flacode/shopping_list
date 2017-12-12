import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
url_prefix = '/api'
POSTGRES = {
    'user': 'postgres',
    'pw': '',
    'db': 'shoppinglistdb',
    'host': 'localhost',
    'port': '5432',
}
DB_URI = 'postgresql://%(user)s:%(pw)s@%(host)s:%(port)s/%(db)s' % POSTGRES
# set debug to true for development purposes
app.config['DEBUG'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
if os.environ.get('DATABASE_URL'):
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = DB_URI
app.config['SECRET_KEY'] = 'this-really-needs-to-be-changed'
db = SQLAlchemy(app)

from app import views, models  # at the end to avoid circular imports

app.register_blueprint(views.api)
