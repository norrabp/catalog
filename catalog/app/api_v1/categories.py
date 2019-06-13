from flask import jsonify, request
from . import api
from .. import db
from ..auth import auth_token
from ..models import Category
from ..schemas import CategorySchema

# Get the urls of all categories
@api.route('/categories', methods=['GET'])
def get_categories_all():
    categories = Category.query.all()
    category_schema = CategorySchema(many=True)
    output = category_schema.dump(categories).data
    return jsonify({'categories': output})

# Create a new category
@api.route('/categories', methods=['POST'])
@auth_token.login_required
def new_category():
    category = Category()
    category.import_data(request.json)
    category_schema = CategorySchema()
    data = category_schema.dump(category).data
    db.session.add(category)
    db.session.commit()
    data['id'] = category.id
    return jsonify(data), 201

# Get a category
@api.route('/categories/<int:id>', methods=['GET'])
def get_category(id):
    category = Category.query.get_or_404(id)
    category_schema = CategorySchema()
    return jsonify(category_schema.dump(category).data)

# Edit a category
@api.route('/categories/<int:id>', methods=['PUT'])
@auth_token.login_required
def edit_category(id):
    category = Category.query.get_or_404(id)
    category.import_data(request.json)
    category_schema = CategorySchema()
    data = category_schema.dump(category).data
    db.session.add(category)
    db.session.commit()
    return jsonify(data)

# Delete a category
@api.route('/categories/<int:id>', methods=['DELETE'])
@auth_token.login_required
def delete_category(id):
    category = Category.query.get_or_404(id)
    db.session.delete(category)
    db.session.commit()
    return jsonify({}), 204
