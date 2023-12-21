import datetime
import os
from dotenv import load_dotenv


load_dotenv()
basedir = os.path.abspath('.')


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    db_name = os.environ.get('SQLALCHEMY_DB_NAME')
    if db_name:
        SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'data', db_name)
    track_modifications = os.environ.get('SQLALCHEMY_TRACK_MODIFICATIONS')
    SQLALCHEMY_TRACK_MODIFICATIONS = track_modifications == "True" if track_modifications else False
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')
    MEDIA_PATH = os.path.join(basedir, 'static', 'media')
    jwt_access_token_expires = os.environ.get('JWT_ACCESS_TOKEN_EXPIRES')
    JWT_ACCESS_TOKEN_EXPIRES = (
        datetime.timedelta(seconds=int(jwt_access_token_expires))
        if jwt_access_token_expires
        else None
    )

class TestConfig:
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get('SECRET_KEY')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')
