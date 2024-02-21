import re
from typing import Optional

from pydantic import BaseModel, validator


class ShopNameValid(BaseModel):
    name: str
    description: Optional[str]
    phone_number: str
    link: Optional[str]
    # TODO
    # Дублювання коду (така сама перевірка здійснюється в accounts)
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
            if not re.match(regex, value) or len(value)>50:
                raise ValueError('Invalid shop name format')
        return value
    
    @validator('description')
    @staticmethod
    def shop_description_validator(value: str) -> str:
        if value is not None:
            regex = r"^[A-Za-zА-ЩЬЮЯҐЄІЇа-щьюяґєії0-9'.,;\- ]+$"
            if not re.match(regex, value) or len(value)>500:
                raise ValueError('Invalid product_detail format')
        return value

    