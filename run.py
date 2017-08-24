import json
from flask import Flask, request, jsonify, make_response
from models import db, Users, ShoppingLists, Items
from werkzeug.security import generate_password_hash, check_password_hash
app = Flask(__name__)
POSTGRES = {
    'user': 'postgres',
    'pw': 'postgres',
    'db': 'shopping_list_tdb1',
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
    data = request.get_json()
    user = Users.query.filter_by(email=data['email']).first()
    if not user:
        new_user = Users(username=data['username'], email=data['email'], password=data['password'])
        new_user.save()
        response = {'message': 'You registered successfully. Please log in.'}
        # return a response notifying the user that they registered successfully
        return make_response(jsonify(response)), 201
    return make_response(jsonify({'message': 'User acccount already exists.'})), 409


@app.route('/auth/login', methods=['POST'])
def login_user():
    """API endpoint to login existing user"""
    auth = request.authorization
    if not auth or not auth.username or not auth.password:
        return make_response('Could not verify user', 401, {'WWW-Authenticate': 'Basic realm ="Login required!"'})
    user = Users.query.filter_by(username=auth.username).first()
    if not user:
        return make_response('User does not exist', 401, {'WWW-Authenticate': 'Basic realm ="Login required!"'})
    if check_password_hash(user.password, auth.password):
        return make_response(jsonify({'message': 'User logged in successfully'})), 200
    return make_response('Invalid user credentials', 401, {'WWW-Authenticate': 'Basic realm ="Login required!"'})


@app.route('/auth/reset-password', methods=['POST'])
def reset_password():
    """API endpoint to change a user's password given a username"""
    data = request.get_json()
    username = data['username']
    user = Users.query.filter_by(username=username).first()
    if not user:
        return make_response(jsonify({'message': 'No user information found'})), 404
    user.password = generate_password_hash(data['password'])
    user.save()
    response = {'message': 'You have successfully changed your password.'}
    # return a response notifying the user that they reset their password successfully
    return make_response(jsonify(response)), 200


@app.route('/shoppinglists/', methods=['POST', 'GET'])
def create_view_shopping_list():
    if request.method == 'POST':
        data = request.get_json()
        new_shopping_list = ShoppingLists(name=data['name'], user_id=data['user_id'], due_date=data['due_date'])
        new_shopping_list.save()
        response = {'message': 'Shopping list created.'}
        return make_response(jsonify(response)), 201
    shopping_lists = ShoppingLists.query.all()
    if shopping_lists == []:
        return make_response(jsonify({'message': 'No shopping lists created yet.'})), 200
    output = []
    for shopping_list in shopping_lists:
        shopping_list_data = {}
        shopping_list_data['id'] = shopping_list.id
        shopping_list_data['name'] = shopping_list.name
        shopping_list_data['due_date'] = shopping_list.due_date
        output.append(shopping_list_data)
    return make_response(jsonify({"shopping_lists": output})), 200


@app.route('/shoppinglists/<id>', methods=['GET'])
def view_one_shopping_list(id):
    shopping_list = ShoppingLists.query.filter_by(id=id).first()
    if shopping_list:
        shopping_list_data = {}
        shopping_list_data['id'] = shopping_list.id
        shopping_list_data['name'] = shopping_list.name
        shopping_list_data['due_date'] = shopping_list.due_date
        return make_response(jsonify(shopping_list_data)), 200
    return make_response(jsonify({"message": "Shopping list can not be found"})), 404


@app.route('/shoppinglists/<id>', methods=['PUT'])
def update_shopping_list(id):
    shopping_list = ShoppingLists.query.filter_by(id=id).first()
    if not shopping_list:
        return make_response(jsonify({"message": "Shopping list can not be found"})), 404
    data = request.get_json()
    if 'name' in json.dumps(data):
        shopping_list.name = data['name']
    if 'due_date' in json.dumps(data):
        shopping_list.due_date = data['due_date']
    shopping_list.save()
    return make_response(jsonify({"message": "Shopping list has been updated"})), 200

@app.route('/shoppinglists/<id>', methods=['DELETE'])
def delete_shopping_list(id):
    shopping_list = ShoppingLists.query.filter_by(id=id).first()
    if not shopping_list:
        return make_response(jsonify({"message": "Shopping list can not be found"})), 404
    shopping_list.delete()
    return make_response(jsonify({"message": "Shopping list successfully deleted"})), 200


@app.route('/shoppinglists/<id>/items/', methods=['POST'])
def add_item_to_shopping_list(id):
    data = request.get_json()
    shopping_list = ShoppingLists.query.filter_by(id=id).first()
    if not shopping_list:
        return make_response(jsonify({"message": "Shopping list can not be found to add items"})), 404
    item = Items(name=data['name'], quantity=data['quantity'],
                 shopping_list_id=id, bought_from=data['bought_from'],
                 status=data['status'])
    item.save()
    return make_response(jsonify({"message": "Item added to shopping list"})), 201

@app.route('/shoppinglists/<id>/items/<item_id>', methods=['PUT'])
def update_item_in_shopping_list(id, item_id):
    data = request.get_json()
    shopping_list = ShoppingLists.query.filter_by(id=id).first()
    item = Items.query.filter_by(id=item_id).first()
    if not shopping_list:
        return make_response(jsonify({"message": "Shopping list can not be found to update items"})), 404
    if not item:
        return make_response(jsonify({"message": "Item can not be found in shopping list"})), 404
    if 'name' in json.dumps(data):
        item.name = data['name']
    if 'quantity' in json.dumps(data):
        item.quantity = data['quantity']
    if 'shopping_list_id' in json.dumps(data):
        new_shopping_list = ShoppingLists.query.filter_by(id=data['shopping_list_id']).first()
        if not new_shopping_list:
            return make_response(jsonify({"message": "Can not move item to not existent shopping list"})), 404
        item.shopping_list_id = data['shopping_list_id']
    if 'bought_from' in data:
        item.bought_from = data['bought_from']
    if 'status' in data:
        item.status = data['status']
    item.save()
    return make_response(jsonify({"message": "Item updated"})), 200


@app.route('/shoppinglists/<id>/items/', methods=['GET'])
def view_items_in_shopping_list(id):
    shopping_list = ShoppingLists.query.filter_by(id=id).first()
    if not shopping_list:
        return make_response(jsonify({"message": "Shopping list can not be found"})), 404
    items = Items.query.filter_by(shopping_list_id=id).all()
    if Items == []:
        return make_response(jsonify({'message': 'Shopping list is empty'})), 200
    output = []
    for item in items:
        item_data = {}
        item_data['id'] = item.id
        item_data['name'] = item.name
        item_data['quantity'] = item.quantity
        item_data['bought_from'] = item.bought_from
        item_data['status'] = item.status
        output.append(item_data)
    return make_response(jsonify({"Items": output})), 200


@app.route('/shoppinglists/<id>/items/<item_id>', methods=['DELETE'])
def delete_item_from_shopping_list(id, item_id):
    shopping_list = ShoppingLists.query.filter_by(id=id).first()
    item = Items.query.filter_by(id=item_id).first()
    if not shopping_list:
        return make_response(jsonify({"message": "Shopping list can not be found to update items"})), 404
    if not item:
        return make_response(jsonify({"message": "Item can not be found in shopping list"})), 404
    item.delete()
    return make_response(jsonify({"message": "Item successfully deleted from shopping list"})), 200


if __name__ == '__main__':
    app.run()
