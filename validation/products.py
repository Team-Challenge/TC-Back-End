from pydantic import BaseModel, validator
from typing import Optional, Dict
from enum import Enum
import re
from flask import abort

class SubCategoryEnum(str, Enum):
    zakolki = 'Заколки'
    obroochi = 'Обручі'
    rezinki = 'Резинки'
    khustinky = 'Хустинки'
    serezhki = 'Сережки'
    monoserezhki = 'Моносережки'
    zghardy= 'Зґарди'
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
    not_available = 'Немає в наявності'

class DeliveryPostEnum(str, Enum):
    nova_post = 'novaPost'
    ukr_post = 'ukrPost'

class MethodOfPaymentEnum(str, Enum):
    card_payment = "cardPayment"
    cash_payment = "cashPayment"
    secure_payment = "securePayment"

class ProductValid(BaseModel):
    category_id: int
    sub_category_name: SubCategoryEnum
    product_name: str
    product_description: Optional[str] = None
    is_active: Optional[bool] = None

class DetailValid(ProductValid):
    price: float
    product_status: Optional[ProductStatusEnum] = None
    product_characteristic: Optional[dict] = None
    is_return: Optional[bool] = None
    delivery_post: Optional[Dict[DeliveryPostEnum, bool]] = None  
    method_of_payment: Optional[Dict[MethodOfPaymentEnum, bool]] = None 
    is_unique: Optional[bool] = None  

    @validator('product_name')
    @staticmethod
    def name_validator(value: str) -> str:
        if value is not None:
            regex = r"^[A-Za-zА-ЩЬЮЯҐЄІЇа-щьюяґєії0-9'.,;\- ]+$"
            if not re.match(regex, value) or len(value)>100:
                raise ValueError('Invalid product_name format')
        return value

    @validator('product_description')
    @staticmethod
    def description_validator(value: str) -> str:
        if value is not None:
            regex = r"^[A-Za-zА-ЩЬЮЯҐЄІЇа-щьюяґєії0-9'.,;\- ]+$"
            if not re.match(regex, value) or len(value)>1000:
                raise ValueError('Invalid product_detail format')
        return value

class UpdateProductValid(BaseModel):
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

def check_sub_category_belongs_to_category(category_id, sub_category_name):
    for category in const_category_list:
        if category['id'] == category_id:
            if sub_category_name in category['subcategories']:
                return True
    abort(400, description=f"'{sub_category_name}' not in category id '{category_id}'")


const_category_list = [
  {
    "id": 1,
    "label": 'На голову',
    "subcategories": ['Заколки', 'Обручі', 'Резинки', 'Хустинки'],
  },
  {
    "id": 2,
    "label": 'На вуха',
    "subcategories": ['Сережки', 'Моносережки'],
  },
  {
    "id": 3,
    "label": 'На шию',
    "subcategories": [
      'Зґарди',
      'Шелести',
      'Ґердани',
      'Силянки',
      'Кризи',
      'Чокери',
      'Намиста',
      'Дукачі',
      'Кулони та підвіски',
    ],
  },
  {
    "id": 4,
    "label": 'На руки',
    "subcategories": ['Браслети', 'Каблучки'],
  },
  {
    "id": 5,
    "label": 'Аксесуари',
    "subcategories": ['Котильйони', 'Брошки', 'Сумки'],
  },
  {
    "id": 6,
    "label": 'Набори',
    "subcategories": ['Набір']
  },
]