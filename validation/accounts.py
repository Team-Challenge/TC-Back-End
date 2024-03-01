import re
from enum import Enum
from typing import Optional

from pydantic import BaseModel, validator


class DeliveryPostEnum(str, Enum):
    nova_post = 'nova_post'
    ukr_post = 'ukr_post'

class PasswordValid(BaseModel):
    password: str

    @validator('password')
    @staticmethod
    def password_validator(value: str) -> str:
        regex = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$"
        if not re.match(regex, value):
            raise ValueError('The password must contain at least one capital letter 8 characters')
        return value

class SigninValid(PasswordValid):    
    email:str

    @validator('email')
    @staticmethod
    def email_validator(value: str) -> str:
        regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        if not re.match(regex, value):
            raise ValueError('Invalid email format')
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
    
class SignupValid(SigninValid, FullNameValid, PasswordValid):
    pass

class PhoneNumberValid(BaseModel):
    phone_number:str

    @validator('phone_number')
    @staticmethod
    def phone_number_validation(value: str) -> str:
        regex = r'^\+380\d{9}$'
        if not re.match(regex, value):
            raise ValueError('Invalid phone number format. Must start with +380 and have 9 digits.')
        return value
    

class DeliveryPostValid(BaseModel):
    owner_id: int
    post: DeliveryPostEnum
    city: str
    branch_name: str
    address: str

class GoogleAuthValid(BaseModel):
    id_token: str

class UserSchema(BaseModel):
    id: int
    full_name: str
    email: str
    profile_picture: Optional[str] = None
    phone_number: Optional[str] = None

    class Config:
        from_attributes = True

class ChangePasswordSchema(BaseModel):
    current_password: str
    new_password: str