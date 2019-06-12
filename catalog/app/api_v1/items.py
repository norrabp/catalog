from flask import jsonify, request
from . import api
from .. import db
from ..auth import auth_token
from ..models import Category, Item
from ..schemas import CategorySchema, ItemSchema


# Get all items in a specific category
@api.route('/categories/<int:id>/items', methods=['GET'])
def get_category_items(id):
    category = Category.query.get_or_404(id)
    category_schema = CategorySchema()
    return jsonify({category.name + ' items': category_schema.dump(category).data['items']})

# Get all items
@api.route('/items', methods=['GET'])
def get_items_all():
    items = Item.query.all()
    item_schema = ItemSchema(many=True)
    return jsonify({'items': item_schema.dump(items).data})

# Get an item
@api.route('/items/<int:id>', methods=['GET'])
def get_item(id):
    item = Item.query.get_or_404(id)
    item_schema = ItemSchema()
    return jsonify(item_schema.dump(item).data)


# Create a new item
@api.route('/categories/<int:id>/items', methods=['POST'])
@auth_token.login_required
def new_item(id):
    item = Item()
    data = request.json
    data['category'] = id
    item.import_data(data)
    db.session.add(item)
    db.session.commit()
    item_schema = ItemSchema()
    return jsonify({}), 201, item_schema.dump(item).data

# Edit an item
@api.route('/items/<int:id>', methods=['PUT'])
@auth_token.login_required
def edit_item(id):
    item = Item.query.get_or_404(id)
    data = request.json
    if 'title' not in data:
        data['title'] = item.title
    if 'category' not in data:
        data['category'] = item.cat_id
    if 'description' not in data:
        data['description'] = item.description
    item.import_data(data)
    db.session.add(item)
    db.session.commit()
    item_schema = ItemSchema()
    return jsonify(item_schema.dump(item).data)

# Delete an item
@api.route('/items/<int:id>', methods=['DELETE'])
@auth_token.login_required
def delete_item(id):
    item = Item.query.get_or_404(id)
    db.session.delete(item)
    db.session.commit()
    return jsonify({}), 204
