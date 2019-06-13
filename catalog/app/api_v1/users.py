from flask import jsonify, request
from . import api
from .. import db
from ..auth import auth
from ..models import User
from ..schemas import UserSchema
from ..exceptions import ValidationError

# Get all users
@api.route('/users', methods=['GET'])
def get_users_all():
    users = User.query.all()
    users_schema = UserSchema(many=True)
    return jsonify({'users': users_schema.dump(users).data})

# Get a specific users
@api.route('/users/<int:id>', methods=['GET'])
def get_user(id):
    user = User.query.get_or_404(id)
    user_schema = UserSchema()
    return jsonify(user_schema.dump(user).data)


# Create a new user
@api.route('/users', methods=['POST'])
def create_user():
    user = User()
    user_schema = UserSchema()
    try:
        user.username = request.json['username']
        user.set_password(request.json['password'])
    except KeyError as e:
        raise ValidationError('Invalid user: missing ' + e.args[0])
    data = user_schema.dump(user).data
    db.session.add(user)
    db.session.commit()
    data['id'] = user.id
    return jsonify({'id': user.id, 'token': user.generate_auth_token()}), 201

# Edit a user
@api.route('/users/<int:id>', methods=['PUT'])
@auth.login_required
def edit_user(id):
    user = User.query.get_or_404(id)
    if auth.username() == user.username or auth.username() == 'Admin':
        if 'username' in request.json:
            user.username = request.json['username']
        if 'password' in request.json:
            user.set_password(request.json['password'])
        db.session.add(user)
        db.session.commit()
        return jsonify({'token': user.generate_auth_token()})
    else:
        response = jsonify({'status': 401, 'error': 'unauthorized', 'message': 'please authenticate'})
        response.status_code = 401
        return response


# Delete a user
@api.route('/users/<int:id>', methods=['DELETE'])
@auth.login_required
def delete_user(id):
    user = User.query.get_or_404(id)
    if auth.username() == user.username or auth.username() == 'Admin':
        db.session.delete(user)
        db.session.commit()
        return jsonify({}), 204
    else:
        response = jsonify({'status': 401, 'error': 'unauthorized', 'message': 'please authenticate'})
        response.status_code = 401
        return response
