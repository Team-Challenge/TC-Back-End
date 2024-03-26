import os

from flask import url_for
from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import mapped_column, relationship

from config import Config
from dependencies import db
from models.errors import NotFoundError
from utils.utils import load_and_save_image, serialize_pydantic_response_error

SHOPS_PHOTOS_PATH = os.path.join(Config.MEDIA_PATH, 'shops')
SHOPS_BANNER_PHOTOS_PATH = os.path.join(Config.MEDIA_PATH, 'banner_shops')


class Shop(db.Model):
    __tablename__ = "shops"

    id = mapped_column(Integer, primary_key=True)
    owner_id = mapped_column(Integer, ForeignKey("users.id"))
    name = mapped_column(String, nullable=False)
    description = mapped_column(String, default=None)
    photo_shop = mapped_column(String, default=None)
    banner_shop = mapped_column(String, default=None)
    phone_number = mapped_column(String, nullable=False)
    link = mapped_column(String, default=None)

    def __init__(self, **kwargs):
        self.owner_id = kwargs.get('owner_id')
        self.name = kwargs.get('name')
        self.description = kwargs.get('description')
        self.photo_shop = kwargs.get('photo_shop')
        self.banner_shop = kwargs.get('banner_shop')
        self.phone_number = kwargs.get('phone_number')
        self.link = kwargs.get('link')

    owner = relationship("User", back_populates="shops")
    shop_to_products = relationship("Product", back_populates="owner_shop")

    @classmethod
    def get_shop_by_owner_id(cls, owner_id):
        return cls.query.filter_by(owner_id=owner_id).first()

    @classmethod
    def create_shop(cls, **data):
        new_shop = cls(**data)
        db.session.add(new_shop)
        db.session.commit()
        return new_shop

    def update_shop_details(self, **data):
        if data.get('name'):
            self.name = data['name']
        if data.get('description'):
            self.description = data['description']
        if data.get('phone_number'):
            self.phone_number = data['phone_number']
        if data.get('link'):
            self.link = data['link']
        db.session.commit()

    def add_photo(self, photo):
        image_path = load_and_save_image(self.photo_shop, photo, SHOPS_PHOTOS_PATH)
        self.photo_shop = image_path
        db.session.commit()
        return image_path

    def add_banner(self, banner):
        image_path = load_and_save_image(self.banner_shop, banner, SHOPS_BANNER_PHOTOS_PATH)
        self.banner_shop = image_path
        db.session.commit()
        return image_path

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

    @classmethod
    def get_shop_user_info(cls, user_id):
        shop = cls.get_shop_by_owner_id(owner_id=user_id)
        if shop is not None:
            shop_info = serialize_pydantic_response_error(shop)
            if shop_info.get("banner_shop") is not None:
                banner_shop_path = url_for('static',
                                           filename=f'media/'
                                                    f'banner_shop/{shop_info["banner_shop"]}',
                                           _external=True)
                shop_info['banner_shop'] = banner_shop_path
            if shop_info.get("photo_shop") is not None:
                photo_shop_path = url_for('static',
                                          filename=f'media/'
                                                   f'shops/{shop_info["photo_shop"]}',
                                          _external=True)
                shop_info['photo_shop'] = photo_shop_path
            return shop_info
        raise NotFoundError('Shop not found')
