import re
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, field_validator

from models.accounts import User

FULL_NAME_REGEX = (
    r"^(?!.*--)(?=.{2,50}$)[A-Za-zА-ЩЬЮЯҐЄІЇа-щьюяґєії''`ʼ\-]+"
    r"( [A-Za-zА-ЩЬЮЯҐЄІЇа-щьюяґєії''`ʼ\-]+)*$"
)
PASSWORD_REGEX = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$"
EMAIL_REGEX = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
PHONE_REGEX = r'^\+380\d{9}$'


class PasswordValidationMixin:
    @field_validator('password')
    @staticmethod
    def password_validator(value: str) -> str:
        if not re.match(PASSWORD_REGEX, value):
            raise ValueError(
                'The password must contain at least one capital letter, '
                'any one number and total 8 characters')
        return value


class FullNameValidationMixin:
    @field_validator('full_name')
    @staticmethod
    def full_name_validator(value: str) -> str:
        if not re.match(FULL_NAME_REGEX, value):
            raise ValueError('Invalid characters in the field full_name')
        return value


class PhoneValidationMixin:
    @field_validator('phone_number')
    @staticmethod
    def phone_number_validation(value: str) -> str:
        if not re.match(PHONE_REGEX, value):
            raise ValueError(
                'Invalid phone number format. Must start with +380 and have 9 digits.')
        return value


class DeliveryPostEnum(str, Enum):
    nova_post = 'nova_post'
    ukr_post = 'ukr_post'


class SigninValid(BaseModel, PasswordValidationMixin):
    email: str
    password: str

    @field_validator('email')
    @staticmethod
    def email_validator(value: str) -> str:
        value = value.lower()
        if not re.match(EMAIL_REGEX, value):
            raise ValueError('Invalid email format')
        return value


class SignupValid(SigninValid, PasswordValidationMixin):
    full_name: str
    email: str
    password: str

    @field_validator('email')
    @staticmethod
    def email_validator(value: str) -> str:
        value = value.lower()
        if not re.match(EMAIL_REGEX, value):
            raise ValueError('Invalid email format')
        existing_email = User.query.filter(User.email == value).first()
        if existing_email:
            raise ValueError('Email is already exists')
        return value

    @field_validator('full_name')
    @staticmethod
    def full_name_validator(value: str) -> str:
        if not re.match(FULL_NAME_REGEX, value):
            raise ValueError('Invalid characters in the field full_name')
        fn = value.split()
        normalized_name = ' '.join(word.capitalize() for word in fn)
        return normalized_name


class PhoneNumberValid(BaseModel, PhoneValidationMixin):
    phone_number: str


class FullNameValid(BaseModel, FullNameValidationMixin):
    full_name: str


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

    model_config = ConfigDict(from_attributes=True)


class UserSignupReturnSchema(BaseModel):
    link: Optional[str]
    user: UserSchema


class ChangePasswordSchema(BaseModel):
    current_password: str
    new_password: str

    @field_validator('new_password')
    @staticmethod
    def password_validator(value: str) -> str:
        if not re.match(PASSWORD_REGEX, value):
            raise ValueError(
                'The password must contain at least one capital letter, '
                'any one number and total 8 characters')
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

    model_config = ConfigDict(from_attributes=True)
