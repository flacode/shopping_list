import json
from flask import jsonify, make_response, request
from werkzeug.security import check_password_hash, generate_password_hash
from app.models import Items, ShoppingLists, Users
from app import app

@app.route('/auth/register', methods=['POST'])
def create_account():
    """API endpoint to create new user"""
    data = request.get_json()
    # check if the username is unique
    user = Users.query.filter_by(username=data['username']).first()
    if not user:
        new_user = Users(username=data['username'], email=data['email'], password=data['password'])
        new_user.save()
        response = {'message': 'You registered successfully. Please log in.'}
        # return a response notifying the user that they registered successfully
        return make_response(jsonify(response)), 201
    return make_response(jsonify({'message': 'User acccount already exists.'})), 202


@app.route('/auth/login', methods=['POST'])
def login_user():
    """API endpoint to login existing user"""
    auth = request.authorization
    # check if auth contains the username and password reqired for login
    if not auth or not auth.username or not auth.password:
        return make_response('Could not verify user', 401, {'WWW-Authenticate': 'Basic realm ="Login required!"'})
    # check if username is for a registered user
    user = Users.query.filter_by(username=auth.username).first()
    if not user:
        return make_response('User does not exist', 401, {'WWW-Authenticate': 'Basic realm ="Login required!"'})
    # compare the hashed password entered in the password and that in stored the database
    if check_password_hash(user.password, auth.password):
        # generate access token for authenticated user
        access_token = user.generate_token(user.id)
        if access_token:
            response = {
                'message': 'User logged in successfully',
                'access_token': access_token.decode()
                }
            return make_response(jsonify(response)), 200
    return make_response('Invalid user credentials', 401, {'WWW-Authenticate': 'Basic realm ="Login required!"'})


@app.route('/auth/reset-password', methods=['POST'])
def reset_password():
    """API endpoint to change a user's password given a username"""
    data = request.get_json()
    # check if username exists in the database
    username = data['username']
    user = Users.query.filter_by(username=username).first()
    if not user:
        return make_response(jsonify({'message': 'No user information found'})), 404
    # hash the password befpre saving it
    user.password = generate_password_hash(data['password'])
    user.save()
    response = {'message': 'You have successfully changed your password.'}
    # return a response notifying the user that they reset their password successfully
    return make_response(jsonify(response)), 200


@app.route('/shoppinglists/', methods=['POST', 'GET'])
def create_view_shopping_list():
    """Method to create or view shopping lists"""
    # get the access token from header
    access_token = request.headers.get('Authorization')
    if access_token:
        # attempt to decode the token and get the User ID
        user_id = Users.decode_token(access_token)
        if not isinstance(user_id, str):
            # handle the request
            if request.method == 'POST':
                data = request.get_json()
                if 'name' in data and 'due_date' in data:
                    new_shopping_list = ShoppingLists(name=data['name'], user_id=user_id, due_date=data['due_date'])
                    new_shopping_list.save()
                    response = {'message': 'Shopping list created.'}
                    return make_response(jsonify(response)), 201
                else:
                    response = {'message': 'Missing attributes, shopping list not created.'}
                    return make_response(jsonify(response)), 400
            else:
                # block for request.method == 'GET'
                key = request.args.get('q', None)
                limit = request.args.get('limit', 10, type=int)
                page = request.args.get('page', 1, type=int)
                # check for a search key
                if key:
                    shopping_lists = ShoppingLists.query.filter(ShoppingLists.name.like("%"+key.strip()+"%")).filter_by(user_id=user_id).order_by(ShoppingLists.due_date).paginate(page, limit, False).items
                else:
                    shopping_lists = ShoppingLists.query.filter_by(user_id=user_id).order_by(ShoppingLists.due_date).paginate(page, limit, False).items
                # create a list of dictionary shopping lists
                output = []
                for shopping_list in shopping_lists:
                    shopping_list_data = {}
                    shopping_list_data['id'] = shopping_list.id
                    shopping_list_data['name'] = shopping_list.name
                    shopping_list_data['due_date'] = shopping_list.due_date
                    output.append(shopping_list_data)
                # check if there are any shopping lists in the database
                if output == []:
                    if key:
                        message = "Shopping list to match the search key not found."
                    else:
                        message = "No shopping lists created yet."
                    return make_response(jsonify({'message': message})), 200
                return make_response(jsonify({"shopping_lists": output})), 200
        else:
            # user is not legit, so the payload is an error message
            message = user_id
            response = {'message': message}
            return make_response(jsonify(response)), 401
    return make_response(jsonify({'message': 'Please register  or login.'})), 401

@app.route('/shoppinglists/<id>', methods=['GET'])
def view_one_shopping_list(id):
    """Get shopping list details by id"""
    # get the access token from header
    access_token = request.headers.get('Authorization')
    if access_token:
        # attempt to decode the token and get the User ID
        user_id = Users.decode_token(access_token)
        if not isinstance(user_id, str):
            # handle the request
            shopping_list = ShoppingLists.query.filter_by(user_id=user_id, id=id).first()
            # check if the shopping list exists in the database
            if shopping_list:
                shopping_list_data = {}
                shopping_list_data['id'] = shopping_list.id
                shopping_list_data['name'] = shopping_list.name
                shopping_list_data['due_date'] = shopping_list.due_date
                return make_response(jsonify({"shopping list": shopping_list_data})), 200
            return make_response(jsonify({"message": "Shopping list can not be found"})), 404
        else:
            # user is not legit, so the payload is an error message
            message = user_id
            response = {'message': message}
            return make_response(jsonify(response)), 401
    return make_response(jsonify({'message': 'Please register  or login.'})), 401

@app.route('/shoppinglists/<id>', methods=['PUT'])
def update_shopping_list(id):
    """Method for user to update shopping_list"""
    # get the access token from header
    access_token = request.headers.get('Authorization')
    if access_token:
        # attempt to decode the token and get the User ID
        user_id = Users.decode_token(access_token)
        if not isinstance(user_id, str):
            # check if shopping list to update exists
            shopping_list = ShoppingLists.query.filter_by(user_id=user_id, id=id).first()
            if not shopping_list:
                return make_response(jsonify({"message": "Shopping list can not be found"})), 404
            data = request.get_json()
            # check if data contains name update
            if 'name' in json.dumps(data):
                shopping_list.name = data['name']
            # check if data contains due_date update
            if 'due_date' in json.dumps(data):
                shopping_list.due_date = data['due_date']
            shopping_list.save()
            return make_response(jsonify({"message": "Shopping list has been updated"})), 200
        else:
            # user is not legit, so the payload is an error message
            message = user_id
            response = {'message': message}
            return make_response(jsonify(response)), 401
    return make_response(jsonify({'message': 'Please register  or login.'})), 401

@app.route('/shoppinglists/<id>', methods=['DELETE'])
def delete_shopping_list(id):
    """Method to delete a shopping list"""
    # get the access token from header
    access_token = request.headers.get('Authorization')
    if access_token:
        # attempt to decode the token and get the User ID
        user_id = Users.decode_token(access_token)
        if not isinstance(user_id, str):
            # check if shopping list to be deleted exists in the database
            shopping_list = ShoppingLists.query.filter_by(user_id=user_id, id=id).first()
            if not shopping_list:
                return make_response(jsonify({"message": "Shopping list can not be found"})), 404
            shopping_list.delete()
            return make_response(jsonify({"message": "Shopping list successfully deleted"})), 200
        else:
            # user is not legit, so the payload is an error message
            message = user_id
            response = {'message': message}
            return make_response(jsonify(response)), 401
    return make_response(jsonify({'message': 'Please register  or login.'})), 401


@app.route('/shoppinglists/<id>/items/', methods=['POST'])
def add_item_to_shopping_list(id):
    # get the access token from header
    access_token = request.headers.get('Authorization')
    if access_token:
        # attempt to decode the token and get the User ID
        user_id = Users.decode_token(access_token)
        if not isinstance(user_id, str):
            # check if shopping list exists in the database
            shopping_list = ShoppingLists.query.filter_by(user_id=user_id, id=id).first()
            if not shopping_list:
                return make_response(jsonify({"message": "Shopping list can not be found to add items"})), 404
            data = request.get_json()
            item = Items(name=data['name'], quantity=data['quantity'],
                         shopping_list_id=id, bought_from=data['bought_from'],
                         status=data['status'])
            item.save()
            return make_response(jsonify({"message": "Item added to shopping list"})), 201
        else:
            # user is not legit, so the payload is an error message
            message = user_id
            response = {'message': message}
            return make_response(jsonify(response)), 401
    return make_response(jsonify({'message': 'Please register  or login.'})), 401


@app.route('/shoppinglists/<id>/items/<item_id>', methods=['PUT'])
def update_item_in_shopping_list(id, item_id):
    # get the access token from header
    access_token = request.headers.get('Authorization')
    if access_token:
        # attempt to decode the token and get the User ID
        user_id = Users.decode_token(access_token)
        if not isinstance(user_id, str):
            # check if shopping list and item exist in the database
            shopping_list = ShoppingLists.query.filter_by(user_id=user_id, id=id).first()
            item = Items.query.filter_by(id=item_id).first()
            if not shopping_list:
                return make_response(jsonify({"message": "Shopping list can not be found to update items"})), 404
            if not item:
                return make_response(jsonify({"message": "Item can not be found in shopping list"})), 404
            # check which parameters have been updated in the request
            data = request.get_json()
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
        else:
            # user is not legit, so the payload is an error message
            message = user_id
            response = {'message': message}
            return make_response(jsonify(response)), 401
    return make_response(jsonify({'message': 'Please register  or login.'})), 401


@app.route('/shoppinglists/<id>/items/', methods=['GET'])
def view_items_in_shopping_list(id):
    """Method to view items in shopping list"""
    # get the access token from header
    access_token = request.headers.get('Authorization')
    if access_token:
        # attempt to decode the token and get the User ID
        user_id = Users.decode_token(access_token)
        if not isinstance(user_id, str):
            shopping_list = ShoppingLists.query.filter_by(user_id=user_id, id=id).first()
            # check if shopping list exists
            if not shopping_list:
                return make_response(jsonify({"message": "Shopping list can not be found"})), 404
            items = Items.query.filter_by(shopping_list_id=id).all()
            # add items to a list of dictionary items
            output = []
            for item in items:
                item_data = {}
                item_data['id'] = item.id
                item_data['name'] = item.name
                item_data['quantity'] = item.quantity
                item_data['bought_from'] = item.bought_from
                item_data['status'] = item.status
                output.append(item_data)
            if output == []:
                return make_response(jsonify({'message': 'Shopping list is empty'})), 200
            return make_response(jsonify({"Items": output})), 200
        else:
            # user is not legit, so the payload is an error message
            message = user_id
            response = {'message': message}
            return make_response(jsonify(response)), 401
    return make_response(jsonify({'message': 'Please register  or login.'})), 401


@app.route('/shoppinglists/<id>/items/<item_id>', methods=['DELETE'])
def delete_item_from_shopping_list(id, item_id):
    """Method to delete items from shopping list"""
    # get the access token from header
    access_token = request.headers.get('Authorization')
    if access_token:
        # attempt to decode the token and get the User ID
        user_id = Users.decode_token(access_token)
        if not isinstance(user_id, str):
            shopping_list = ShoppingLists.query.filter_by(user_id=user_id, id=id).first()
            item = Items.query.filter_by(id=item_id).first()
            # validate if shopping list and item exist
            if not shopping_list:
                return make_response(jsonify({"message": "Shopping list can not be found to update items"})), 404
            if not item:
                return make_response(jsonify({"message": "Item can not be found in shopping list"})), 404
            item.delete()
            return make_response(jsonify({"message": "Item successfully deleted from shopping list"})), 200
        else:
            # user is not legit, so the payload is an error message
            message = user_id
            response = {'message': message}
            return make_response(jsonify(response)), 401
    return make_response(jsonify({'message': 'Please register  or login.'})), 401