import datetime
import os
from dotenv import load_dotenv


load_dotenv()
basedir = os.path.abspath('.')


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'data',
                                                          os.environ.get('SQLALCHEMY_DB_NAME'))
    SQLALCHEMY_TRACK_MODIFICATIONS = os.environ.get(
        'SQLALCHEMY_TRACK_MODIFICATIONS') == "True"
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')
    MEDIA_PATH = os.path.join(basedir, 'static', 'media')
    JWT_ACCESS_TOKEN_EXPIRES = datetime.timedelta(seconds=int(os.environ.get('JWT_ACCESS_TOKEN_EXPIRES')))
    FULL_NAME_PATTERN = os.environ.get('FULL_NAME_PATTERN')
    PHONE_NUMBER_PATTERN = os.environ.get('PHONE_NUMBER_PATTERN')
    NAME_SHOP_PATTERN = os.environ.get('NAME_SHOP_PATTERN')
    PASSWORD_PATTERN = os.environ.get('PASSWORD_PATTERN')

class TestConfig:
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get('SECRET_KEY')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')
