from datetime import datetime
from app import db, ma
from marshmallow import fields, Schema, validate, ValidationError
from datetime import datetime
from sqlalchemy.orm import mapped_column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import relationship
from sqlalchemy import Integer, String, DateTime, Boolean


class User(db.Model):
    __tablename__ = "users"

    def __init__(self, email, full_name):
        self.email = email
        self.full_name = full_name

    id = mapped_column(Integer, primary_key=True)
    full_name = mapped_column(String)
    email = mapped_column(String)
    joined_at = mapped_column(DateTime, default=datetime.utcnow())
    is_active = mapped_column(Boolean, default=False)
    profile_picture = mapped_column(String)
    phone_number = mapped_column(String, default=None)


class Product(db.Model):
    __tablename__ = "products"

    def __init__(self, name):
        self.name = name

    id = mapped_column(Integer, primary_key=True)
    name = mapped_column(String(36))
    description = mapped_column(String(512))
    seller_id = mapped_column(Integer, ForeignKey('shops.id'))
    category_id = mapped_column(Integer, ForeignKey('product_categories.id'))
    price = mapped_column(Integer)
    is_avaliable = mapped_column(Boolean)


class Order(db.Model):
    __tablename__ = "orders"

    def __init__(self, user_id):
        self.user_id = user_id
        self.date = datetime.utcnow()

    id = mapped_column(Integer, primary_key=True)
    user_id = mapped_column(String, ForeignKey("users.id"))
    date = mapped_column(DateTime)
    status_id = mapped_column(String, ForeignKey('order_statuses.id'))
    comment = mapped_column(String)
    delivery_address = mapped_column(String)

    products: Mapped[list["ProductOrder"]] = relationship()


class OrderStatus(db.Model):
    __tablename__ = "order_statuses"
    id = mapped_column(Integer, primary_key=True)
    status = mapped_column(String(24))


class Shop(db.Model):
    __tablename__ = "shops"

    def __init__(self, owner_id, name):
        self.owner_id = owner_id
        self.name = name

    id = mapped_column(Integer, primary_key=True)
    owner_id = mapped_column(String, ForeignKey("users.id"))
    name = mapped_column(String)
    

class ProductOrder(db.Model):
    __tablename__ = "product_order"

    def __init__(self, order_id, product_id, amount):
        self.order_id = order_id
        self.product_id = product_id
        self.amount = amount

    order_id = mapped_column(ForeignKey('orders.id'), primary_key=True)
    product_id = mapped_column(ForeignKey('products.id'), primary_key=True)
    amount = mapped_column(Integer)
    product: Mapped["Product"] = relationship()


class Security(db.Model):
    __tablename__ = "security"

    def __init__(self, password):
        self.password_hash = password

    user_id = mapped_column(Integer, ForeignKey(
        "users.id"), primary_key=True)
    password_hash = mapped_column(String(64))


class ProductCategory(db.Model):
    __tablename__ = "product_categories"

    id = mapped_column(Integer, primary_key=True)
    name = mapped_column(String)
    description = mapped_column(String)


class ProductPhoto(db.Model):
    __tablename__ = "products_photos"

    id = mapped_column(Integer, primary_key=True)
    product_id = mapped_column(Integer, ForeignKey('products.id'))
    picture_id = mapped_column(String(64))


def email_is_unique(email):
    if User.query.filter_by(email=email).first():
        raise ValidationError('User with such email already exist')
