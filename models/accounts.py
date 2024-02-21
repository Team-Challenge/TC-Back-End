
from datetime import datetime
from typing import List

from flask_jwt_extended import get_jwt_identity
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from dependencies import db
from models.products import ProductComment
from models.shops import Shop


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

class DeliveryUserInfo(db.Model):
    __tablename__ = "delivery_user_info"

    id = mapped_column(Integer, primary_key=True)
    owner_id = mapped_column(Integer, ForeignKey("users.id"))
    post = mapped_column(String, default=None)
    city = mapped_column(String, default=None)
    branch_name = mapped_column(String, default=None)
    address = mapped_column(String, default=None)

    owner: Mapped["User"] = relationship(
        "User", back_populates="delivery_user_info")

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