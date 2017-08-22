from flask_api import FlaskAPI
from models import db
app = FlaskAPI(__name__, instance_relative_config=True)
POSTGRES = {
    'user': 'postgres',
    'pw': 'postgres',
    'db': 'shopping_guru_db1',
    'host': 'localhost',
    'port': '5432',
}
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://%(user)s:\
%(pw)s@%(host)s:%(port)s/%(db)s' % POSTGRES
SECRET_KEY = 'this-really-needs-to-be-changed'
db.init_app(app)  # connect sqlalchmey to app


@app.route('/')
def hello():
    return "Hello world"


if __name__ == '__main__':
    app.run()
