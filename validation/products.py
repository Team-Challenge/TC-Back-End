import datetime
import json
import os.path
import re
from enum import Enum
from pathlib import Path
from typing import Dict, Optional

from flask import url_for
from pydantic import BaseModel, ConfigDict, field_validator


class SubCategoryEnum(str, Enum):
    zakolki = 'Заколки'
    obroochi = 'Обручі'
    rezinki = 'Резинки'
    khustinky = 'Хустинки'
    serezhki = 'Сережки'
    monoserezhki = 'Моносережки'
    zghardy = 'Зґарди'
    shelesti = 'Шелести'
    herdany = 'Ґердани'
    sylianky = 'Силянки'
    kryzi = 'Кризи'
    chokery = 'Чокери'
    namysta = 'Намиста'
    dukachi = 'Дукачі'
    kulony_ta_pidvisky = 'Кулони та підвіски'
    braslety = 'Браслети'
    kabluchky = 'Каблучки'
    kotyliony = 'Котильйони'
    broshky = 'Брошки'
    sumky = 'Сумки'
    set_cub_category = 'Набір'


class ProductStatusEnum(str, Enum):
    in_availability = 'В наявності'
    to_order = 'Під замовлення'
    unique_instance = 'В єдиному екземплярі'
    not_available = 'Нема в наявності'


class DeliveryPostEnum(str, Enum):
    nova_post = 'novaPost'
    ukr_post = 'ukrPost'


class MethodOfPaymentEnum(str, Enum):
    card_payment = "cardPayment"
    cash_payment = "cashPayment"
    secure_payment = "securePayment"


class CreateProductValid(BaseModel):
    category_id: int
    sub_category_id: int
    product_name: str
    product_description: Optional[str] = None
    is_active: Optional[bool] = None
    price: float
    product_status: Optional[ProductStatusEnum] = None
    product_characteristic: Optional[dict] = None
    is_return: Optional[bool] = None
    delivery_post: Optional[Dict[DeliveryPostEnum, bool]] = None
    method_of_payment: Optional[Dict[MethodOfPaymentEnum, bool]] = None
    is_unique: Optional[bool] = None

    @field_validator('product_name')
    @staticmethod
    def name_validator(value: str) -> str:
        if value is not None:
            regex = r"^[A-Za-zА-ЩЬЮЯҐЄІЇа-щьюяґєії0-9'.,;\- ]+$"
            if not re.match(regex, value) or len(value) > 100:
                raise ValueError('Invalid product_name format')
        return value

    @field_validator('product_description')
    @staticmethod
    def description_validator(value: str) -> str:
        if value is not None:
            regex = r"^[A-Za-zА-ЩЬЮЯҐЄІЇа-щьюяґєії0-9'.,;\- ]+$"
            if not re.match(regex, value) or len(value) > 1000:
                raise ValueError('Invalid product_detail format')
        return value


class UpdateProductValid(BaseModel):
    product_id: int
    product_name: Optional[str] = None
    price: Optional[float] = None
    product_description: Optional[str] = None
    is_active: Optional[bool] = None
    product_status: Optional[ProductStatusEnum] = None
    product_characteristic: Optional[dict] = None
    is_return: Optional[bool] = None
    delivery_post: Optional[Dict[DeliveryPostEnum, bool]] = None
    method_of_payment: Optional[Dict[MethodOfPaymentEnum, bool]] = None
    is_unique: Optional[bool] = None

    @field_validator('product_name')
    @staticmethod
    def name_validator(value: str) -> str:
        if value is not None:
            regex = r"^[A-Za-zА-ЩЬЮЯҐЄІЇа-щьюяґєії0-9'.,;\- ]+$"
            if not re.match(regex, value) or len(value) > 100:
                raise ValueError('Invalid product_name format')
        return value

    @field_validator('product_description')
    @staticmethod
    def description_validator(value: str) -> str:
        if value is not None:
            regex = r"^[A-Za-zА-ЩЬЮЯҐЄІЇа-щьюяґєії0-9'.,;\- ]+$"
            if not re.match(regex, value) or len(value) > 1000:
                raise ValueError('Invalid product_detail format')
        return value


class PhotoProductValid(BaseModel):
    product_photo: str
    main: bool


class ProductPhotoSchema(BaseModel):
    id: int
    product_photo: str
    timestamp: datetime.datetime
    main: bool

    model_config = ConfigDict(from_attributes=True)

    @field_validator("product_photo", mode="after")
    @classmethod
    def set_product_photo(cls, v):
        image = url_for('static', filename=f'media/products/{v}',
                        _external=True)
        return image


class ProductInfoSchema(BaseModel):
    id: int
    product_name: str
    price: float
    product_status: Optional[ProductStatusEnum] = None
    is_unique: Optional[bool]
    photo: Optional[ProductPhotoSchema] = None

    model_config = ConfigDict(from_attributes=True)


class DetailProductInfoSchema(BaseModel):
    id: int
    category_id: int
    sub_category_id: int
    shop_id: int
    product_name: str
    product_description: Optional[str]
    price: float
    time_added: datetime.datetime
    time_modifeid: datetime.datetime
    is_active: bool
    is_return: Optional[bool]
    is_unique: Optional[bool]
    product_status: Optional[ProductStatusEnum] = None
    product_characteristic: Optional[dict]
    delivery_post: Optional[dict]
    method_of_payment: Optional[dict]
    photos: list[ProductPhotoSchema]


class PaginatedDetailProductSchema(BaseModel):
    has_previous: bool = False
    has_next: bool = False
    total_pages: int = 0
    data: list[DetailProductInfoSchema]


class PaginatedProductSchema(BaseModel):
    has_previous: bool = False
    has_next: bool = False
    total_pages: int = 0
    data: list[ProductInfoSchema]


def get_subcategory_name(category_id, subcategory_id):
    static_path = os.path.join(
        Path(__file__).parent.parent, "static/categories/categories.json")
    with open(static_path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    if str(category_id) not in data:
        raise ValueError('The category with the specified ID does not exist')

    subcategories = data[str(category_id)]['subcategories']
    subcategory_name = subcategories.get(str(subcategory_id))

    if subcategory_name is None:
        raise ValueError(
            'The subcategory with the specified ID does not belong to the category')

    return subcategory_name


def get_subcategory_id(subcategory_name):
    static_path = os.path.join(
        Path(__file__).parent.parent, "static/categories/categories.json")
    with open(static_path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    for _, category_data in data.items():
        subcategories = category_data.get('subcategories', {})
        for subcategory_id, name in subcategories.items():
            if name == subcategory_name:
                return int(subcategory_id)

    raise ValueError('The subcategory with the specified name does not exist')
