from flask import Flask, request, jsonify, make_response
from models import db, Users
from werkzeug.security import generate_password_hash, check_password_hash
app = Flask(__name__)
POSTGRES = {
    'user': 'postgres',
    'pw': 'postgres',
    'db': 'shopping_list_tdb',
    'host': 'localhost',
    'port': '5432',
}
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://%(user)s:\
%(pw)s@%(host)s:%(port)s/%(db)s' % POSTGRES
SECRET_KEY = 'this-really-needs-to-be-changed'
db.init_app(app)  # connect sqlalchmey to app


@app.route('/auth/register', methods=['POST'])
def create_account():
    """API endpoint to create new user"""
    print(request.data)
    data = request.get_json()
    new_user = Users(username=data['username'], email=data['email'], password=data['password'])
    new_user.save()
    response = {'message': 'You registered successfully. Please log in.'}
    # return a response notifying the user that they registered successfully
    return make_response(jsonify(response)), 201


@app.route('/auth/login', methods=['POST'])
def login_user():
    auth = request.authorization
    print(auth)
    if not auth or not auth.username or not auth.password:
        return make_response('Could not verify user', 401, {'WWW-Authenticate': 'Basic realm ="Login required!"'})
    user = Users.query.filter_by(username=auth.username).first()
    if not user:
        return make_response('Could not verify user', 401, {'WWW-Authenticate': 'Basic realm ="Login required!"'})
    if check_password_hash(user.password, auth.password):
        return make_response(jsonify({'message': 'User logged in successfully'})), 201
    return make_response('Could not verify user', 401, {'WWW-Authenticate': 'Basic realm ="Login required!"'})


# @app.route('/auth/reset-password')

if __name__ == '__main__':
    app.run()

