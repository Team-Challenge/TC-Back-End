import os
import uuid
from datetime import datetime

from sqlalchemy import (Boolean, DateTime, Float, ForeignKey, Integer, String,
                        Text)
from sqlalchemy.orm import mapped_column, relationship

from config import Config
from dependencies import db
from models.accounts import User
from models.errors import NotFoundError, UserError
from models.shops import Shop
from utils.utils import product_info_serialize
from validation.products import get_subcategory_name

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

    category = relationship("Categories",
                                                    back_populates="product")
    product_to_comment = relationship("ProductComment",
                                                                back_populates="product_comment")
    owner_shop = relationship("Shop", back_populates="shop_to_products")
    product_to_detail = relationship("ProductDetail",
                                                              back_populates="product_detail")
    
    def __init__(self, shop_id, **kwargs):
        self.category_id = kwargs.get('category_id')
        self.sub_category_name = kwargs.get('sub_category_name')
        self.shop_id = shop_id
        self.product_name = kwargs.get('product_name')
        self.product_description = kwargs.get('product_description')
        self.is_active = kwargs.get('is_active', True)
        self.time_added = datetime.now()
        self.time_modifeid = datetime.now()

    # TODO: return success or error message. Remove all flask imports in this file++++
    # TODO: jsonify should be called in route++++++
    @staticmethod
    def delete_product(product_id):
        user = User.get_user_id()
        if user is not None:
            shop = Shop.get_shop_by_owner_id(user.id)
            if shop is not None:
                product = Product.get_product_by_id(product_id)
                if product is not None and product.shop_id == shop.id:
                    product.is_active = False
                    db.session.commit()
                    return {"message": "Ok"}
                raise UserError('Product not found or permission not granted')
            raise NotFoundError('Shop not found')
        raise NotFoundError('User not found')

    # TODO: return success or error message. Remove all flask imports in this file++++++
    # TODO: jsonify should be called in route+++++++++
    @classmethod
    def add_product(cls, **kwargs):
        user = User.get_user_id()
        if user is not None:
            # TODO: Remove unnecessary exception
            try:
                kwargs['sub_category_name'] = get_subcategory_name(kwargs.get('category_id'),
                                                                kwargs.get('sub_category_id'))
            except ValueError as e:
                raise ValueError(e) from e
            shop = Shop.get_shop_by_owner_id(user.id)
            if shop is not None:
                product = cls(shop.id, **kwargs)
                db.session.add(product)
                db.session.flush()
                ProductDetail.add_product_detail(product_id=product.id, **kwargs)
                return {'message': 'The product was created successfully'}
            raise NotFoundError('Shop not found')
        raise NotFoundError('User not found')

    @classmethod
    def get_product_by_id(cls, product_id):
        return cls.query.filter_by(id=product_id).first()

    # TODO: return success or error message. Remove all flask imports in this file++++
    # TODO: jsonify should be called in route++++
    @staticmethod
    def update_product(**kwargs):
        user = User.get_user_id()
        if user is not None:      
            product = Product.query.get(kwargs.get('product_id'))
            shop = Shop.get_shop_by_owner_id(user.id)
            if shop is not None or product is not None:
                try:
                    if product and product.shop_id == shop.id:
                        for key, value in kwargs.items():
                            setattr(product, key, value)
                        product.time_modified = datetime.now()
                        ProductDetail.update_product_detail(**kwargs)
                        return {"message": "Product updated successfully"}
                    raise UserError('Product not found or not belong to shop')
                except UserError as e:
                    raise UserError(e) from e
            raise NotFoundError('Shop or product not found')
        raise NotFoundError('User not found')
        

        
class ProductPhoto(db.Model):
    __tablename__ = "product_photos"

    id = mapped_column(Integer, primary_key=True)
    product_detail_id = mapped_column(
        Integer, ForeignKey('product_details.id'))
    product_photo = mapped_column(String)
    timestamp = mapped_column(DateTime)
    main = mapped_column(Boolean, default=False)

    product_image = relationship("ProductDetail",
                                                          back_populates="product_to_photo")

    def __init__(self, product_detail_id, product_photo, main):
        self.timestamp = datetime.now()
        self.product_detail_id = product_detail_id
        self.product_photo = product_photo
        self.main = main

    # TODO: return success or error message. Remove all flask imports in this file+++++
    # TODO: jsonify should be called in route++++++++
    @classmethod
    def add_product_photo(cls, product_id, photo, main):
        user = User.get_user_id()
        if user is not None:
            product = Product.get_product_by_id(product_id)
            product_detail = ProductDetail.get_product_detail_by_product_id(product.id)
            if product is None or product_detail is None:
                raise NotFoundError('Product not found')
            num_photos = ProductPhoto.get_num_photos_by_product_detail_id(product_detail.id)
            if num_photos >= 4:
                return {'error': 'The maximum photos for product has been 4'}
            allowed_extensions = {'png', 'jpg', 'jpeg', 'webp'}
            if '.' in photo.filename and photo.filename.rsplit(
                                        '.', 1)[1].lower() in allowed_extensions:
                file_extension = photo.filename.split('.')[-1]
                file_name = uuid.uuid4().hex
                file_path = os.path.join(
                    PRODUCT_PHOTOS_PATH, f"{file_name}.{file_extension}")
                photo.save(file_path)

                new_photo = cls(product_detail_id=product_detail.id,
                            product_photo=f"{file_name}.{file_extension}", main=main)
                db.session.add(new_photo)
                db.session.commit()
                return {"message": "Photo product uploaded successfully"}
            raise UserError('Bad request')
        raise NotFoundError('User not found')

    @classmethod
    def get_num_photos_by_product_detail_id(cls, product_detail_id):
        return cls.query.filter_by(product_detail_id=product_detail_id).count()

    def remove_product_photo(self):
        file_path = os.path.join(PRODUCT_PHOTOS_PATH, self.product_photo)
        if os.path.isfile(file_path):
            os.remove(file_path)
        db.session.delete(self)
        db.session.commit()

    def serialize(self):
        return {
                "id": self.id,
                "product_photo": self.product_photo,
                "timestamp": self.timestamp.isoformat(),
                "main": self.main
                }

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

    product_detail = relationship("Product", back_populates="product_to_detail")
    product_to_photo = relationship("ProductPhoto",back_populates="product_image",
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

    # TODO: return success or error message. Remove all flask imports in this file++++
    # TODO: jsonify should be called in route++++
    @staticmethod
    def update_product_detail(**kwargs):
        product_detail = ProductDetail.query.filter_by(product_id=kwargs['product_id']).first()
        if product_detail is None:
            return {"error": "Product detail not found"}
        
        for key, value in kwargs.items():
            setattr(product_detail, key, value)
    
        db.session.commit()
        return {"message": "Product detail updated"}


class ProductComment(db.Model):
    __tablename__ = "product_comment"

    id = mapped_column(Integer, primary_key=True)
    product_id = mapped_column(Integer, ForeignKey("products.id"))
    user_id = mapped_column(Integer, ForeignKey("users.id"))
    comment = mapped_column(String(200))
    raiting = mapped_column(Float)
    time_added = mapped_column(DateTime)
    is_confirmed_purchase = mapped_column(Boolean, default=False)

    product_comment = relationship("Product",
                                                      back_populates="product_to_comment")
    user_comment = relationship("User", back_populates="comment")

    def __init__(self, user_id, product_id, comment, raiting):
        self.user_id = user_id
        self.product_id = product_id
        self.comment = comment
        self.raiting = raiting
        self.time_added = datetime.utcnow()

class Categories(db.Model):
    __tablename__ = "categories"

    id = mapped_column(Integer, primary_key=True)
    category_name = mapped_column(String, unique=True)

    product = relationship("Product", back_populates="category")

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

# TODO: return success or error message. Remove all flask imports in this file++++++++
# TODO: jsonify should be called in route+++++++++
def get_all_shop_products():
    user = User.get_user_id()
    if user is not None:
        shop = Shop.get_shop_by_owner_id(user.id)
        if not shop:
            return {'error': 'Shop not found'}
        try:
            shop_products = db.session.query(Product, ProductDetail, ProductPhoto) \
                .join(ProductDetail, Product.id == ProductDetail.product_id) \
                .outerjoin(ProductPhoto, ProductDetail.id == ProductPhoto.product_detail_id) \
                .filter(Product.shop_id == shop.id) \
                .all()
            response = product_info_serialize(shop_products)
            return response
        except ValueError as e:
            raise ValueError(e) from e
    raise NotFoundError('User not found')
