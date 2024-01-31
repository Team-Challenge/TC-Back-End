from pydantic import BaseModel, validator
from typing import Optional
from enum import Enum
import re

class SubCategoryEnum(str, Enum):
    zakolki = 'заколки'
    obroochi = 'обручі'
    rezinki = 'резинки'
    khustinky = 'хустинки'
    serezhki = 'сережки'
    monoserezhki = 'моносережки'
    zghardy = 'згарди'
    shelesti = 'шелести'
    herdany = 'гердани'
    sylianky = 'силянки'
    kryzi = 'кризи'
    chokery = 'чокери'
    namysta = 'намиста'
    dukachi = 'дукачі'
    kulony_ta_pidvisky = 'кулони та підвіски'
    braslety = 'браслети'
    kabluchky = 'каблучки'
    kotyliony = 'котильйони'
    broshky = 'брошки'
    sumky = 'сумки'

class ProductStatus(str, Enum):
    in_availability = 'В наявності'
    to_order = 'Під замовлення'
    unique_instance = 'В єдиному екземплярі'
    not_available = 'Немає в наявності'

class Delivery_Post(str, Enum):
    nova_post = 'nova_post'
    ukr_post = 'ukr_post'

class ProductValid(BaseModel):
    category_id: int
    sub_category_name: SubCategoryEnum
    product_name: str
    product_description: Optional[str] = None
    is_active: Optional[bool] = None

class DetailValid(ProductValid):
    price: float
    product_status: Optional[ProductStatus] = None
    product_characteristic: Optional[dict] = None
    is_return: Optional[bool] = None
    delivery_post: Optional[Delivery_Post] = None  
    method_of_payment: Optional[str] = None 
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
    category_id: Optional[int] = None
    sub_category_name: Optional[SubCategoryEnum] = None
    product_name: Optional[str] = None
    price: Optional[float] = None
    product_description: Optional[str] = None
    is_active: Optional[bool] = None
    product_status: Optional[ProductStatus] = None
    product_characteristic: Optional[dict] = None
    is_return: Optional[bool] = None
    delivery_post: Optional[Delivery_Post] = None
    method_of_payment: Optional[str] = None 
    is_unique: Optional[bool] = None