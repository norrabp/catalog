from flask import current_app
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, BadSignature
from . import db
from .exceptions import ValidationError


# User Model
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    password_hash = db.Column(db.String(128))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_auth_token(self, expires_in=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expires_in=expires_in)
        return s.dumps({'id': self.id}).decode('utf-8')

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except BadSignature:
            return None
        return User.query.get(data['id'])


# Item Database Model
class Category(db.Model):
    # Create the database table for categories.
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True, nullable=None)
    items = db.relationship('Item', backref='category', lazy='dynamic')

    def import_data(self, data):
        try:
            self.name = data['name']
        except KeyError as e:
            raise ValidationError('Invalid customer: missing ' + e.args[0])
        return self


# Item Database Model
class Item(db.Model):
    __tablename__ = 'items'
    id = db.Column(db.Integer, primary_key=True)
    cat_id = db.Column(db.Integer, db.ForeignKey('categories.id'),
                       index=True, nullable=False)
    title = db.Column(db.String(64), index=True, nullable=False, unique=True)
    description = db.Column(db.String(1000))

    def import_data(self, data):
        try:
            self.title = data['title']
            self.description = data['description']
            self.cat_id = data['category']
        except KeyError as e:
            raise ValidationError('Invalid order: missing ' + e.args[0])
        return self
