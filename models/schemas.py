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
from models.models import User, Order, Product, ProductOrder, email_is_unique


class UserSchema(ma.SQLAlchemyAutoSchema):
    email = fields.Email()
    class Meta:
        model = User


class SigninUserSchema(Schema):
    email = fields.Email()
    password = fields.Str()
    

class SignupUserSchema(Schema):
    email = fields.Email(validate=lambda x: email_is_unique(x))
    full_name = fields.Str(validate=validate.Length(min=2, max=50))
    password = fields.Str(validate=validate.Regexp('^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$'))


class UserInfoSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
        exclude = ('id', 'joined_at', 'is_active')


class PhoneChangeSchema(Schema):
    phone_number = fields.Str(validate=validate.Length(min=3))


class FullNameChangeSchema(Schema):
    full_name = fields.Str(validate=validate.Length(min=2, max=50))


class PasswordChangeSchema(Schema):
    current_password = fields.Str()
    new_password = fields.Str(validate=validate.Regexp('^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$'))


class ProductSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Product
        load_instance = True
        include_relationships = True


class ProductOrderSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = ProductOrder
        load_instance = True
        include_relationships = True
    product = fields.Nested(ProductSchema)


class OrderSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Order
        load_instance = True
        include_relationships = True
    products = fields.Nested(ProductOrderSchema, many=True)
