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
from models.patterns import SubCategoryEnum, Delivery_Post, ProductStatus
from sqlalchemy import Integer, String, DateTime, Boolean, Float, Text
from typing import List
from flask_jwt_extended import get_jwt_identity


SHOPS_PHOTOS_PATH = os.path.join(Config.MEDIA_PATH, 'shops')
SHOPS_BANNER_PHOTOS_PATH = os.path.join(Config.MEDIA_PATH, 'banner_shops')
PRODUCT_PHOTOS_PATH = os.path.join(Config.MEDIA_PATH, 'products')

class User(db.Model):
    __tablename__ = "users"

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
    comment: Mapped[List["ProductComment"]] = relationship("ProductComment",
                                                                back_populates="user_comment")

    def __init__(self, email, full_name):
        self.email = email
        self.full_name = full_name

    @classmethod
    def get_user_id(cls):
        current_user_id = get_jwt_identity()
        return User.query.filter_by(id=current_user_id).first()


class Security(db.Model):
    __tablename__ = "security"

    user_id = mapped_column(Integer, ForeignKey("users.id"), primary_key=True)
    password_hash = mapped_column(String(64))

    def __init__(self, password):
        self.password_hash = password

class Product(db.Model):
    __tablename__ = "products"

    id = mapped_column(Integer, primary_key=True)
    category_id = mapped_column(Integer, ForeignKey('categories.id'))
    sub_category_name = mapped_column(SubCategoryEnum)
    shop_id = mapped_column(Integer, ForeignKey('shops.id'))
    product_name = mapped_column(String(100))
    product_description = mapped_column(String(1000), default=None)
    time_added = mapped_column(DateTime, default=None)
    time_modifeid = mapped_column(DateTime, default=None)
    is_active = mapped_column(Boolean, default=True)

    def __init__(self, shop_id, **kwargs):
        self.category_id = kwargs.get('category_id')
        self.sub_category_name = kwargs.get('sub_category_name')
        self.shop_id = shop_id
        self.product_name = kwargs.get('product_name')
        self.product_description = kwargs.get('product_description')
        self.is_active = kwargs.get('is_active', True)
        self.time_added = kwargs.get('time_added', None)
        self.time_modifeid = kwargs.get('time_modifeid')

    categories: Mapped["Categories"] = relationship("Categories",
                                                            back_populates="products")
    product_to_comment: Mapped["ProductComment"] = relationship("ProductComment",
                                                            back_populates="product_comment")
    product_to_raiting: Mapped["ProductRaiting"] = relationship("ProductRaiting",
                                                            back_populates="product_raiting")
    owner_shop: Mapped["Shop"] = relationship("Shop", back_populates="shop_to_products")
    product_to_detail: Mapped["ProductDetail"] = relationship("ProductDetail",
                                                        back_populates="product_detail")
    @staticmethod
    def delete_product(product_id):
        product = Product.query.get(product_id)
        if product:
            product.is_active = False
            db.session.commit()
                                                        
    @classmethod
    def add_product(cls, shop_id, **kwargs):
        time_added = datetime.utcnow()
        time_modifeid = datetime.utcnow()
        kwargs['time_added'] = time_added
        kwargs['time_modifeid'] = time_modifeid
        product = cls(shop_id, **kwargs)
        db.session.add(product)
        db.session.commit()
        return product

    @classmethod
    def get_product_by_id(cls, product_id):
        return cls.query.filter_by(id=product_id).first()
    
    def update_product(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        self.time_modifeid = datetime.utcnow()
        db.session.commit()

class Shop(db.Model):
    __tablename__ = "shops"

    id = mapped_column(Integer, primary_key=True)
    owner_id = mapped_column(Integer, ForeignKey("users.id"))
    name = mapped_column(String)
    description = mapped_column(String, default=None)
    photo_shop = mapped_column(String, default=None )
    banner_shop = mapped_column(String, default=None)
    phone_number = mapped_column(String, default=None)
    link = mapped_column(String, default=None)

    def __init__(self, **kwargs):
        self.owner_id = kwargs.get('owner_id')
        self.name = kwargs.get('name')
        self.description = kwargs.get('description')
        self.photo_shop = kwargs.get('photo_shop')
        self.banner_shop = kwargs.get('banner_shop')
        self.phone_number = kwargs.get('phone_number')
        self.link = kwargs.get('link')


    owner: Mapped["User"] = relationship("User", back_populates="shops")
    shop_to_products: Mapped["Product"] = relationship("Product", back_populates="owner_shop")

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


class Categories(db.Model):
    __tablename__ = "categories"

    id = mapped_column(Integer, primary_key=True)
    category_name = mapped_column(String)

    products: Mapped[List["Product"]] = relationship("Product", back_populates="categories")

    def __init__(self, category_name):
        self.category_name = category_name

    @classmethod
    def create_category(cls, category_name):
        new_category = cls(category_name=category_name)
        db.session.add(new_category)
        db.session.commit()
        return new_category

    @staticmethod
    def get_all_categories():
        categories = Categories.query.all()
        return categories

    def as_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}


class ProductPhoto(db.Model):
    __tablename__ = "product_photos"

    id = mapped_column(Integer, primary_key=True)
    product_detail_id = mapped_column(Integer, ForeignKey('product_details.id'))
    product_photo = mapped_column(String)
    timestamp = mapped_column(DateTime)
    main = mapped_column(Boolean, default=False)

    product_image: Mapped["ProductDetail"] = relationship("ProductDetail",
                                                        back_populates="product_to_photo")

    def __init__(self, product_detail_id, product_photo, main):
        self.timestamp = datetime.utcnow()
        self.product_detail_id = product_detail_id
        self.product_photo = product_photo
        self.main = main

    @classmethod
    def add_product_photo(cls, product_detail_id, photo, main):
        file_extension = photo.filename.split('.')[-1]
        file_name = uuid.uuid4().hex
        file_path = os.path.join(PRODUCT_PHOTOS_PATH, f"{file_name}.{file_extension}")

        photo.save(file_path)

        new_photo = cls(product_detail_id=product_detail_id, 
                                product_photo=f"{file_name}.{file_extension}", main=main)
        db.session.add(new_photo)
        db.session.commit()

        return new_photo
        
    def serialize(self):
        return {
                "id": self.id,
                "product_photo": self.product_photo,
                "timestamp": self.timestamp.isoformat(),
                "main": self.main
                }

    def remove_product_photo(self):
        file_path = os.path.join(PRODUCT_PHOTOS_PATH, self.product_photo)
        if os.path.isfile(file_path):
            os.remove(file_path)
        db.session.delete(self)
        db.session.commit()

class DeliveryUserInfo(db.Model):
    __tablename__ = "delivery_user_info"

    id = mapped_column(Integer, primary_key=True)
    owner_id = mapped_column(Integer, ForeignKey("users.id"))
    post = mapped_column(String, default=None)
    city = mapped_column(String, default=None)
    branch_name = mapped_column(String, default=None)
    address = mapped_column(String, default=None)

    owner: Mapped["User"] = relationship("User", back_populates="delivery_user_info")

    def __init__(self, **kwargs):
        self.owner_id = kwargs.get('owner_id')
        self.post = kwargs.get('post')
        self.city = kwargs.get('city')
        self.branch_name = kwargs.get('branch_name')
        self.address = kwargs.get('address')

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

class ProductDetail(db.Model):
    __tablename__ = "product_details"

    id = mapped_column(Integer, primary_key=True)
    product_id = mapped_column(Integer, ForeignKey("products.id"))
    price = mapped_column(Float)
    product_status = mapped_column(ProductStatus, default=None)
    product_characteristic = mapped_column(Text, default=None)
    is_return = mapped_column(Boolean, default=False)
    delivery_post = mapped_column(Delivery_Post, default=None)
    method_of_payment = mapped_column(String, default=None)
    is_unique = mapped_column(Boolean, default=False)

    product_detail: Mapped["Product"] = relationship("Product", back_populates="product_to_detail")
    product_to_photo: Mapped[List["ProductPhoto"]] = relationship(
        "ProductPhoto",
        back_populates="product_image",
        lazy="joined",
        uselist=True
    )

    def __init__(self, **kwargs):
        self.product_id = kwargs.get('product_id')
        self.price = kwargs.get('price')
        self.product_status = kwargs.get('product_status')
        self.product_characteristic = kwargs.get('product_characteristic')
        self.is_return = kwargs.get('is_return')
        self.delivery_post = kwargs.get('delivery_post')
        self.method_of_payment = kwargs.get('method_of_payment')
        self.is_unique = kwargs.get('is_unique')

    @classmethod
    def add_product_detail(cls, product_id, **kwargs):
        product_detail = cls(product_id=product_id, **kwargs)
        db.session.add(product_detail)
        db.session.commit()
        return product_detail

    @classmethod
    def get_product_detail_by_id(cls, product_detail_id):
        return cls.query.filter_by(id=product_detail_id).first()

    def update_product_detail(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        db.session.commit()

    def serialize(self):
        return {
            "id": self.id,
            "product_id": self.product_id,
            "price": self.price,
            "product_status": self.product_status,
            "product_characteristic": self.product_characteristic,
            "is_return": self.is_return,
            "delivery_post": self.delivery_post,
            "method_of_payment": self.method_of_payment,
            "is_unique": self.is_unique,
            "photos": [photo.serialize() for photo in self.product_to_photo],
        }


class ProductRaiting(db.Model):
    __tablename__ = 'product_raitings'

    id = mapped_column(Integer, primary_key=True)
    product_id = mapped_column(Integer, ForeignKey("products.id"))
    product_rating = mapped_column(Float)
    votes = mapped_column(Integer, default=0)

    product_raiting: Mapped["Product"] = relationship("Product", 
                                                        back_populates="product_to_raiting")

    def __init__(self, product_id, product_rating):
        self.product_id = product_id
        self.product_rating = product_rating

class ProductComment(db.Model):
    __tablename__ = "product_comment"

    id = mapped_column(Integer, primary_key=True)
    product_id = mapped_column(Integer, ForeignKey("products.id"))
    user_id = mapped_column(Integer, ForeignKey("users.id"))
    comment = mapped_column(String(200)) 

    product_comment: Mapped["Product"] = relationship("Product",
                                                     back_populates="product_to_comment")
    user_comment: Mapped["User"] = relationship("User", back_populates="comment")

    def __init__(self, user_id, product_id, comment):
        self.user_id = user_id
        self.product_id = product_id
        self.comment = comment

def email_is_unique(email):
    if User.query.filter_by(email=email).first():
        raise ValidationError('User with such email already exist') 

def full_name_validation(full_name):
    if not re.match(r"^[a-zA-Zа-яА-ЯґҐєЄіІї-'`Ї\s]+$",full_name):
        raise ValidationError('Invalid characters in the field full_name')

def phone_validation(phone_number):
    if not re.match(r'^\+380\d{9}$', phone_number):
        raise ValueError('Invalid phone number format. Must start with +380 and have 9 digits.')
