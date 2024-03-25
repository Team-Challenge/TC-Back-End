import re
from typing import Optional

from pydantic import BaseModel, validator, ConfigDict
from sqlalchemy import func

from models.shops import Shop
from validation.products import PaginatedProductSchema


class ShopCreateValid(BaseModel):
    owner_id: int
    name: str
    description: Optional[str]
    phone_number: str
    link: Optional[str]

    @validator('phone_number')
    @staticmethod
    def phone_number_validation(value: str) -> str:
        regex = r'^\+380\d{9}$'
        if not re.match(regex, value):
            raise ValueError('Invalid phone number format. Must start with +380 and have 9 digits.')
        return value

    @validator('name')
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

    @validator('description')
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

    @validator('phone_number')
    @staticmethod
    def phone_number_validation(value: str) -> str:
        regex = r'^\+380\d{9}$'
        if not re.match(regex, value):
            raise ValueError('Invalid phone number format. Must start with +380 and have 9 digits.')
        return value

    @validator('name')
    @staticmethod
    def shop_name_validator(value: str, values) -> str:
        owner_id = values.get('owner_id')
        if value is not None:
            regex = r"^[A-Za-zА-ЩЬЮЯҐЄІЇа-щьюяґєії0-9'.,;\- ]+$"
            if not re.match(regex, value) or len(value) > 50:
                raise ValueError('Invalid shop name format')
            existing_shop = Shop.query.filter(func.lower(Shop.name) == value.lower()).first()
            user_shop = Shop.query.filter(Shop.owner_id == owner_id).first()
            if existing_shop and existing_shop != user_shop:
                raise ValueError('Shop with this name already exists')
        return value

    @validator('description')
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


class ShopWithProductsSchema(ShopSchema):
    products: PaginatedProductSchema
