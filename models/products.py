import os
import uuid
from datetime import datetime
from typing import List

from flask import abort, jsonify
from marshmallow import ValidationError
from sqlalchemy import (Boolean, DateTime, Float, ForeignKey, Integer, String,
                        Text)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from config import Config
from dependencies import db
from validation.products import DetailValid, UpdateProductValid

PRODUCT_PHOTOS_PATH = os.path.join(Config.MEDIA_PATH, 'products')

class Product(db.Model):
    __tablename__ = "products"

    id = mapped_column(Integer, primary_key=True)
    category_id = mapped_column(Integer, ForeignKey('categories.id'))
    sub_category_name = mapped_column(String)
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
        self.time_added = datetime.utcnow()
        self.time_modifeid = datetime.utcnow()

    categories: Mapped["Categories"] = relationship("Categories",
                                                    back_populates="products")
    product_to_comment: Mapped["ProductComment"] = relationship("ProductComment",
                                                                back_populates="product_comment")
    owner_shop: Mapped["Shop"] = relationship(
        "Shop", back_populates="shop_to_products")
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


class ProductPhoto(db.Model):
    __tablename__ = "product_photos"

    id = mapped_column(Integer, primary_key=True)
    product_detail_id = mapped_column(
        Integer, ForeignKey('product_details.id'))
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
        file_path = os.path.join(
            PRODUCT_PHOTOS_PATH, f"{file_name}.{file_extension}")

        photo.save(file_path)

        new_photo = cls(product_detail_id=product_detail_id,
                        product_photo=f"{file_name}.{file_extension}", main=main)
        db.session.add(new_photo)
        db.session.commit()

        return new_photo

    @classmethod
    def get_num_photos_by_product_detail_id(cls, product_detail_id):
        return cls.query.filter_by(product_detail_id=product_detail_id).count()

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

class ProductDetail(db.Model):
    __tablename__ = "product_details"

    id = mapped_column(Integer, primary_key=True)
    product_id = mapped_column(Integer, ForeignKey("products.id"))
    price = mapped_column(Float)
    product_status = mapped_column(String, default=None)
    product_characteristic = mapped_column(Text, default=None)
    is_return = mapped_column(Boolean, default=False)
    delivery_post = mapped_column(Text, default=None)
    method_of_payment = mapped_column(Text, default=None)
    is_unique = mapped_column(Boolean, default=False)

    product_detail: Mapped["Product"] = relationship(
        "Product", back_populates="product_to_detail")
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
    def get_product_detail_by_product_id(cls, product_id):
        return cls.query.filter_by(product_id=product_id).first()

    def validate_product_data(data):
        try:
            validated_data = UpdateProductValid(
                **data).model_dump(exclude_none=True)
            if validated_data.get('product_name'):
                DetailValid.name_validator(
                    value=validated_data.get('product_name'))
            if validated_data.get('product_description'):
                DetailValid.description_validator(
                    value=validated_data.get('product_description'))
            return validated_data
        except ValidationError as e:
            abort(400, description=str(e))
        except ValueError as e:
            return jsonify({"error": str(e)}), 400

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


class ProductComment(db.Model):
    __tablename__ = "product_comment"

    id = mapped_column(Integer, primary_key=True)
    product_id = mapped_column(Integer, ForeignKey("products.id"))
    user_id = mapped_column(Integer, ForeignKey("users.id"))
    comment = mapped_column(String(200))
    raiting = mapped_column(Float)
    time_added = mapped_column(DateTime)
    is_confirmed_purchase = mapped_column(Boolean, default=False)

    product_comment: Mapped["Product"] = relationship("Product",
                                                      back_populates="product_to_comment")
    user_comment: Mapped["User"] = relationship(
        "User", back_populates="comment")

    def __init__(self, user_id, product_id, comment, raiting):
        self.user_id = user_id
        self.product_id = product_id
        self.comment = comment
        self.raiting = raiting
        self.time_added = datetime.utcnow()