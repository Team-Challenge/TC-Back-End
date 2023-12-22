import os
import re
import uuid

from datetime import datetime
from dependencies import db
from marshmallow import ValidationError
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from config import Config
from sqlalchemy import Integer, String, DateTime, Boolean
from typing import List
from flask_jwt_extended import get_jwt_identity


SHOPS_PHOTOS_PATH = os.path.join(Config.MEDIA_PATH, 'shops')
SHOPS_BANNER_PHOTOS_PATH = os.path.join(Config.MEDIA_PATH, 'banner_shops')

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
    delivery_user_info: Mapped[List["DeliveryUserInfo"]] = relationship("DeliveryUserInfo",
                                                                        back_populates="owner")

    @classmethod
    def get_user_id(cls):
        current_user_id = get_jwt_identity()
        return User.query.filter_by(id=current_user_id).first()


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

    def __init__(self, **kwargs):

        self.owner_id = kwargs.get('owner_id')
        self.name = kwargs.get('name')
        self.description = kwargs.get('description')
        self.photo_shop = kwargs.get('photo_shop')
        self.banner_shop = kwargs.get('banner_shop')
        self.phone_number = kwargs.get('phone_number')
        self.link = kwargs.get('link')


    id = mapped_column(Integer, primary_key=True)
    owner_id = mapped_column(Integer, ForeignKey("users.id"))
    name = mapped_column(String)
    description = mapped_column(String, default=None)
    photo_shop = mapped_column(String, default=None )
    banner_shop = mapped_column(String, default=None)
    phone_number = mapped_column(String, default=None)
    link = mapped_column(String, default=None)

    owner: Mapped["User"] = relationship("User", back_populates="shops")

    @classmethod
    def get_shop_by_owner_id(cls, owner_id):
        return cls.query.filter_by(owner_id=owner_id).first()

    @classmethod
    def create_shop(cls, owner_id, name, phone_number, **kwargs):
        new_shop = cls(owner_id=owner_id, name=name, phone_number=phone_number, **kwargs)
        db.session.add(new_shop)
        db.session.commit()
        return new_shop

    def update_shop_details(self, name=None, description=None, phone_number=None, link=None):
        if name:
            self.name = name
        if description:
            self.description = description
        if phone_number:
            self.phone_number = phone_number
        if link:
            self.link = link
        db.session.commit()
    
    def add_photo(self, photo):
        file_extension = photo.filename.split('.')[-1]
        file_name = uuid.uuid4().hex
        file_path = os.path.join(SHOPS_PHOTOS_PATH, f"{file_name}.{file_extension}")

        if self.photo_shop:
            old_file_path = os.path.join(SHOPS_PHOTOS_PATH, self.photo_shop)
            if os.path.isfile(old_file_path):
                os.remove(old_file_path)

        self.photo_shop = f"{file_name}.{file_extension}"
        photo.save(file_path)
        db.session.commit()

    def add_banner(self, banner):
        file_extension = banner.filename.split('.')[-1]
        file_name = uuid.uuid4().hex
        file_path = os.path.join(SHOPS_BANNER_PHOTOS_PATH, f"{file_name}.{file_extension}")

        if self.banner_shop:
            old_file_path = os.path.join(SHOPS_BANNER_PHOTOS_PATH, self.banner_shop)
            if os.path.isfile(old_file_path):
                os.remove(old_file_path)

        self.banner_shop = f"{file_name}.{file_extension}"
        banner.save(file_path)
        db.session.commit()

    def remove_photo(self):
        file_path = os.path.join(SHOPS_PHOTOS_PATH, self.photo_shop)
        if os.path.isfile(file_path):
            os.remove(file_path)
        self.photo_shop = None
        db.session.commit()

    def remove_banner(self):
        file_path = os.path.join(SHOPS_BANNER_PHOTOS_PATH, self.banner_shop)
        if os.path.isfile(file_path):
            os.remove(file_path)
        self.banner_shop = None
        db.session.commit()


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

class DeliveryUserInfo(db.Model):
    __tablename__ = "delivery_user_info"

    def __init__(self, **kwargs):
        self.owner_id = kwargs.get('owner_id')
        self.post = kwargs.get('post')
        self.city = kwargs.get('city')
        self.branch_name = kwargs.get('branch_name')
        self.address = kwargs.get('address')

    id = mapped_column(Integer, primary_key=True)
    owner_id = mapped_column(Integer, ForeignKey("users.id"))
    post = mapped_column(String, default=None)
    city = mapped_column(String, default=None)
    branch_name = mapped_column(String, default=None)
    address = mapped_column(String, default=None)

    owner: Mapped["User"] = relationship("User", back_populates="delivery_user_info")

    @classmethod
    def get_delivery_info_by_owner_id(cls, owner_id):
        return cls.query.filter_by(owner_id=owner_id).first()

    @classmethod
    def add_delivery_info(cls, **kwargs):
        new_delivery_address = cls(**kwargs)
        db.session.add(new_delivery_address)
        db.session.commit()
        return new_delivery_address

    def update_delivery_info(self, post=None, city=None, branch_name=None, address=None):
        if post:
            self.post = post
        if city:
            self.city = city
        if branch_name:
            self.branch_name = branch_name
        if address:
            self.address = address
        db.session.commit()

    def remove_delivery_info(self):
        db.session.delete(self)
        db.session.commit()


def email_is_unique(email):
    if User.query.filter_by(email=email).first():
        raise ValidationError('User with such email already exist') 

def full_name_validation(full_name):
    if not re.match(r"^[a-zA-Zа-яА-ЯґҐєЄіІїЇ\s]+$",full_name):
        raise ValidationError('Invalid characters in the field full_name')

def phone_validation(phone_number):
    if not re.match(r'^\+380\d{9}$', phone_number):
        raise ValueError('Invalid phone number format. Must start with +380 and have 9 digits.')