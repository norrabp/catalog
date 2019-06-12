from . import ma
from .models import Category, Item, User

# User Marshmallow schema
class UserSchema(ma.ModelSchema):
    class Meta:
        model = User

# Category Marshmallow schema
class CategorySchema(ma.ModelSchema):
    class Meta:
        model = Category


# Item Marshmallow Schema
class ItemSchema(ma.ModelSchema):
    class Meta:
        model = Item