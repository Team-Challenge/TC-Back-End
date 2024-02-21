import re

from marshmallow import ValidationError
from pydantic import BaseModel, validator


class SigninValid(BaseModel):
    email:str
    password:str

    @validator('email')
    @staticmethod
    def email_validator(value: str) -> str:
        regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        if not re.match(regex, value):
            raise ValueError('Invalid email format')
        return value
    
    @validator('password')
    @staticmethod
    def password_validator(value: str) -> str:
        regex = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$"
        if not re.match(regex, value):
            raise ValueError('The password must contain at least one capital letter and at least 8 characters')
        return value

class FullNameValid(BaseModel):
    full_name:str

    @validator('full_name')
    @staticmethod
    def full_name_validator(value: str) -> str:
        regex = r"^[a-zA-Zа-яА-ЯґҐєЄіІїЇ'\-]+(?:\s[a-zA-Zа-яА-ЯґҐєЄіІїЇ'\-]+)*$"
        if not re.match(regex, value):
            raise ValueError('Invalid characters in the field full_name')
        return value
    

class SignupValid(SigninValid, FullNameValid):

    @classmethod
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)

        cls.__annotations__.update(SigninValid.__annotations__)
        cls.__annotations__.update(FullNameValid.__annotations__)
        cls.__validators__.update(SigninValid.__validators__)
        cls.__validators__.update(FullNameValid.__validators__)

class PhoneNumberValid(BaseModel):
    phone_number:str

    @validator('phone_number')
    @staticmethod
    def phone_number_validation(value: str) -> str:
        regex = r'^\+380\d{9}$'
        if not re.match(regex, value):
            raise ValueError('Invalid phone number format. Must start with +380 and have 9 digits.')
        return value
    

