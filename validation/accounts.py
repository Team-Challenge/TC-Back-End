import re
from enum import Enum
from typing import Optional

from pydantic import BaseModel, validator

from models.accounts import User


class DeliveryPostEnum(str, Enum):
    nova_post = 'nova_post'
    ukr_post = 'ukr_post'


class SigninValid(BaseModel):
    email: str
    password: str

    @validator('password')
    @staticmethod
    def password_validator(value: str) -> str:
        regex = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$"
        if not re.match(regex, value):
            raise ValueError('The password must contain at least one capital letter 8 characters')
        return value

    @validator('email')
    @staticmethod
    def email_validator(value: str) -> str:
        regex = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(regex, value):
            raise ValueError('Invalid email format')
        return value


class SignupValid(SigninValid):
    full_name: str
    email: str
    password: str

    @validator('full_name')
    @staticmethod
    def full_name_validator(value: str) -> str:
        regex = r"^(?=.{2,50}$)[A-Za-zА-ЩЬЮЯҐЄІЇа-щьюяґєії''`ʼ\-]+( [A-Za-zА-ЩЬЮЯҐЄІЇа-щьюяґєії''`ʼ\-]+)*$"
        if not re.match(regex, value):
            raise ValueError('Invalid characters in the field full_name')
        return value

    @validator('password')
    @staticmethod
    def password_validator(value: str) -> str:
        regex = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$"
        if not re.match(regex, value):
            raise ValueError('The password must contain at least one capital letter 8 characters')
        return value

    @validator('email')
    @staticmethod
    def email_validator(value: str) -> str:
        regex = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(regex, value):
            raise ValueError('Invalid email format')
        existing_email = User.query.filter(User.email == value).first()
        if existing_email:
            raise ValueError('Email is already exists')
        return value


class PhoneNumberValid(BaseModel):
    phone_number: str

    @validator('phone_number')
    @staticmethod
    def phone_number_validation(value: str) -> str:
        regex = r'^\+380\d{9}$'
        if not re.match(regex, value):
            raise ValueError('Invalid phone number format. Must start with +380 and have 9 digits.')
        return value


class FullNameValid(BaseModel):
    full_name: str

    @validator('full_name')
    @staticmethod
    def full_name_validator(value: str) -> str:
        regex = r"^(?=.{2,50}$)[A-Za-zА-ЩЬЮЯҐЄІЇа-щьюяґєії''`ʼ\-]+( [A-Za-zА-ЩЬЮЯҐЄІЇа-щьюяґєії''`ʼ\-]+)*$"
        if not re.match(regex, value):
            raise ValueError('Invalid characters in the field full_name')
        return value


class DeliveryPostValid(BaseModel):
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

    @validator('new_password')
    @staticmethod
    def password_validator(value: str) -> str:
        regex = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$"
        if not re.match(regex, value):
            raise ValueError('The password must contain at least one capital letter 8 characters')
        return value


class UserInfoSchema(BaseModel):
    full_name: str
    email: str
    profile_picture: Optional[str] = None
    phone_number: Optional[str] = None
    post: Optional[str] = None
    city: Optional[str] = None
    branch_name: Optional[str] = None
    address: Optional[str] = None
    shop_id: Optional[int] = None
    have_a_shop: Optional[bool] = False

    class Config:
        from_attributes = True
