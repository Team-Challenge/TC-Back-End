
import re

from datetime import datetime
from dependencies import db
from marshmallow import ValidationError
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy import Integer, String, DateTime, Boolean,UniqueConstraint
from typing import List


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

    shops: Mapped["Shop"] = relationship("Shop", back_populates="owner")


class Security(db.Model):
    __tablename__ = "security"

    def __init__(self, password):
        self.password_hash = password

    user_id = mapped_column(Integer, ForeignKey("users.id"), primary_key=True)
    password_hash = mapped_column(String(64))


class Product(db.Model):
    __tablename__ = "products"

    def __init__(self, name):
        self.name = name

    id = mapped_column(Integer, primary_key=True)
    name = mapped_column(String(36))
    description = mapped_column(String(512))
    seller_id = mapped_column(Integer, ForeignKey('shops.id'))
    category_id = mapped_column(Integer, ForeignKey('product_category.id'))
    price = mapped_column(Integer)
    is_avaliable = mapped_column(Boolean)


class Order(db.Model):
    __tablename__ = "orders"

    def __init__(self, user_id):
        self.user_id = user_id
        self.date = datetime.utcnow()

    id = mapped_column(Integer, primary_key=True)
    user_id = mapped_column(Integer, ForeignKey("users.id"))
    date = mapped_column(DateTime)
    status_id = mapped_column(String, ForeignKey('order_status.id'))
    comment = mapped_column(String)
    delivery_address = mapped_column(String)

    products: Mapped[List["ProductOrder"]] = relationship()


class OrderStatus(db.Model):
    __tablename__ = "order_status"
    id = mapped_column(Integer, primary_key=True)
    status = mapped_column(String(24))


class Shop(db.Model):
    __tablename__ = "shops"

    def __init__(self, name=None, description=None, photo_shop=None, banner_shop=None, phone_number=None, owner_id=None):
        
        self.owner_id = owner_id
        self.name = name
        self.description = description
        self.photo_shop = photo_shop
        self.banner_shop = banner_shop
        self.phone_number = phone_number

    id = mapped_column(Integer, primary_key=True)
    owner_id = mapped_column(Integer, ForeignKey("users.id"))
    name = mapped_column(String)
    description = mapped_column(String, default=None)
    photo_shop = mapped_column(String, default=None )
    banner_shop = mapped_column(String, default=None)
    phone_number = mapped_column(String, default=None)


    owner: Mapped["User"] = relationship("User", back_populates="shops")
    links: Mapped["Link"] = relationship("Link", back_populates="shop")

class Link(db.Model):
    __tablename__ = "links"

    def __init__(self, shop_id, title, link):
        self.shop_id = shop_id
        self.title = title
        self.link = link
        
    id = mapped_column(Integer, primary_key=True)
    title = mapped_column(String, nullable=False)
    link = mapped_column(String, nullable=False)
    shop_id = mapped_column(Integer, ForeignKey("shops.id"))

    shop: Mapped["Shop"] = relationship("Shop", back_populates="links")


class ProductOrder(db.Model):
    __tablename__ = "product_order"

    def __init__(self, order_id, product_id, amount):
        self.order_id = order_id
        self.product_id = product_id
        self.amount = amount

    order_id = mapped_column(ForeignKey('orders.id'), primary_key=True)
    product_id = mapped_column(ForeignKey('products.id'), primary_key=True)
    unit_price = mapped_column(Integer)
    amount = mapped_column(Integer)
    product: Mapped["Product"] = relationship()


class ProductCategory(db.Model):
    __tablename__ = "product_category"

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

def full_name_validation(full_name):
    if not re.match(r"^[a-zA-Zа-яА-ЯґҐєЄіІїЇ\s]+$",full_name):
        raise ValidationError('Invalid characters in the field full_name')