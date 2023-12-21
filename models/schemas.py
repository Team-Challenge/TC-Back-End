from marshmallow import fields, Schema, validate

from dependencies import ma
from models.models import (User,
                        Order,
                        Product,
                        ProductOrder,
                        email_is_unique,
                        Shop,
                        DeliveryUserInfo)


class UserSchema(ma.SQLAlchemyAutoSchema):
    email = fields.Email()
    class Meta:
        model = User


class SigninUserSchema(Schema):
    email = fields.Email()
    password = fields.Str()
    

class SignupUserSchema(Schema):
    email = fields.Email(validate=email_is_unique)
    full_name = fields.Str(validate=validate.Regexp(r"^[a-zA-Zа-яА-ЯґҐєЄіІїЇ\s]+$"))
    password = fields.Str(validate=validate.Regexp(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$", error='invalid'))  # noqa: W605


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
    new_password = fields.Str(validate=validate.Regexp('^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$'))    # noqa: W605


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

class ShopSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Shop
        include_relationships = True
        load_instance = True

class ShopInfoPhotoShema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Shop
        exclude = ("id", "owner_id", "name", "description", "banner_shop", "phone_number", "link")

class ShopInfoBannerShema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Shop
        exclude = ("id", "owner_id", "name", "description", "photo_shop", "phone_number", "link")

class UserDeliveryInfoSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = DeliveryUserInfo
        include_relationships = True
        load_instance = True
