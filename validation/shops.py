import re
from typing import Optional

from flask import url_for
from pydantic import BaseModel, ConfigDict, field_validator
from pydantic_core.core_schema import ValidationInfo
from sqlalchemy import func

from models.shops import Shop
from validation.products import PaginatedProductSchema, ProductInfoSchema


class ShopCreateValid(BaseModel):
    owner_id: int
    name: str
    description: Optional[str]
    phone_number: str
    link: Optional[str]

    @field_validator('phone_number')
    @staticmethod
    def phone_number_validation(value: str) -> str:
        regex = r'^\+380\d{9}$'
        if not re.match(regex, value):
            raise ValueError('Invalid phone number format. Must start with +380 and have 9 digits.')
        return value

    @field_validator('name')
    @staticmethod
    def shop_name_validator(value: str) -> str:
        if value is not None:
            regex = r"^[A-Za-zА-ЩЬЮЯҐЄІЇа-щьюяґєії0-9'.,;\- ]+$"
            if not re.match(regex, value) or len(value) > 50:
                raise ValueError('Invalid shop name format')
            existing_shop = Shop.query.filter(func.lower(Shop.name) == value.lower()).first()
            if existing_shop:
                raise ValueError('Shop with this name already exists')
        return value

    @field_validator('description')
    @staticmethod
    def shop_description_validator(value: str) -> str:
        if value is not None:
            regex = r"^[A-Za-zА-ЩЬЮЯҐЄІЇа-щьюяґєії0-9'.,;\- ]+$"
            if not re.match(regex, value) or len(value) > 500:
                raise ValueError('Invalid product_detail format')
        return value


class ShopUpdateValid(BaseModel):
    owner_id: int
    name: Optional[str] = None
    description: Optional[str] = None
    phone_number: Optional[str] = None
    link: Optional[str] = None

    @field_validator('phone_number')
    @staticmethod
    def phone_number_validation(value: str) -> str:
        regex = r'^\+380\d{9}$'
        if not re.match(regex, value):
            raise ValueError('Invalid phone number format. Must start with +380 and have 9 digits.')
        return value

    @field_validator('name')
    @staticmethod
    def shop_name_validator(value: str, values: ValidationInfo) -> str:
        owner_id = values.data.get('owner_id')
        if value is not None:
            regex = r"^[A-Za-zА-ЩЬЮЯҐЄІЇа-щьюяґєії0-9'.,;\- ]+$"
            if not re.match(regex, value) or len(value) > 50:
                raise ValueError('Invalid shop name format')
            existing_shop = Shop.query.filter(func.lower(Shop.name) == value.lower()).first()
            user_shop = Shop.query.filter(Shop.owner_id == owner_id).first()
            if existing_shop and existing_shop != user_shop:
                raise ValueError('Shop with this name already exists')
        return value

    @field_validator('description')
    @staticmethod
    def shop_description_validator(value: str) -> str:
        if value is not None:
            regex = r"^[A-Za-zА-ЩЬЮЯҐЄІЇа-щьюяґєії0-9'.,;\- ]+$"
            if not re.match(regex, value) or len(value) > 500:
                raise ValueError('Invalid product_detail format')
        return value


class ShopSchema(BaseModel):
    id: int
    owner_id: int
    name: str
    description: Optional[str] = None
    photo_shop: Optional[str] = None
    banner_shop: Optional[str] = None
    phone_number: str
    link: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

    @field_validator("photo_shop", mode="after")
    @classmethod
    def set_photo_shop(cls, v):
        if v:
            image = url_for('static', filename=f'media/shops/{v}',
                            _external=True)
            return image
        return v

    @field_validator("banner_shop", mode="after")
    @classmethod
    def set_banner_shop(cls, v):
        if v:
            image = url_for('static', filename=f'media/banner_shops/{v}',
                            _external=True)
            return image
        return v


class ShopWithProductsSchema(BaseModel):
    shop: ShopSchema
    products: PaginatedProductSchema

    @classmethod
    def load_list(cls, item_list, shop):
        result = []
        shop = ShopSchema.model_validate(shop)
        for product_tuple in item_list:
            product_id = product_tuple[0]
            product_name = product_tuple[1]
            price = product_tuple[2]
            product_status = product_tuple[3]
            is_unique = product_tuple[4]
            photo = product_tuple[5]

            schema = ProductInfoSchema(id=product_id,
                                       product_name=product_name,
                                       price=price,
                                       product_status=product_status,
                                       is_unique=is_unique,
                                       photo=photo)
            result.append(schema)
        return cls(shop=shop, products=PaginatedProductSchema(data=result))
