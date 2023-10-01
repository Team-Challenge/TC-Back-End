from datetime import datetime
from app import db, ma
from marshmallow import fields, Schema, validate, ValidationError


class User(db.Model):
    __tablename__ = "users"

    def __init__(self, email, full_name):
        self.email = email
        self.full_name = full_name

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(50))
    email = db.Column(db.String(50))
    joined_at = db.Column(db.DateTime, default=datetime.utcnow())
    is_active = db.Column(db.Boolean, default=False)
    profile_picture = db.Column(db.String(64))


class Shop(db.Model):
    __tablename__ = "shops"

    def __init__(self, owner_id, name):
        self.owner_id = owner_id
        self.name = name

    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.String(50), db.ForeignKey("users.id"))
    name = db.Column(db.String(50))

class ProductCategory(db.Model):
    __tablename__ = "product_categories"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(36))
    description = db.Column(db.String(512))

class Product(db.Model):
    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(36))
    description = db.Column(db.String(512))
    seller_id = db.Column(db.Integer, db.ForeignKey('shops.id'))
    category_id = db.Column(db.Integer, db.ForeignKey('product_categories.id'))
    price = db.Column(db.Integer)
    is_avaliable = db.Column(db.Boolean)

class ProductPhoto(db.Model):
    __tablename__ = "products_photos"

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'))
    picture_id = db.Column(db.String(64))

class OrderStatus(db.Model):
    __tablename__ = "order_statuses"
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(24))

class Order(db.Model):
    __tablename__ = "orders"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(50), db.ForeignKey("users.id"))
    date = db.Column(db.DateTime)
    status_id = db.Column(db.String, db.ForeignKey('order_statuses.id'))
    total_price = db.Column(db.Integer)
    comment = db.Column(db.String(512))
    delivery_address = db.Column(db.String(128))


class OrderProducts(db.Model):
    __tablename__ = "order_products"

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'))
    products_id = db.Column(db.Integer, db.ForeignKey('products.id'))
    amount = db.Column(db.Integer)

class Security(db.Model):
    __tablename__ = "security"

    def __init__(self, password):
        self.password_hash = password

    user_id = db.Column(db.Integer, db.ForeignKey(
        "users.id"), primary_key=True)
    password_hash = db.Column(db.String(64))


class UserSchema(ma.SQLAlchemyAutoSchema):
    email = fields.Email()
    class Meta:
        model = User

class UserInfoSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
        exclude = ('id', 'joined_at', 'is_active')

class SignupUserSchema(Schema):
    email = fields.Email(validate=lambda x: email_is_unique(x))
    full_name = fields.Str(validate=validate.Length(min=2, max=50))
    password = fields.Str(validate=validate.Length(min=8))


class SigninUserSchema(Schema):
    email = fields.Email()
    password = fields.Str()


def email_is_unique(email):
    if User.query.filter_by(email=email).first():
        raise ValidationError('User with such email already exist')