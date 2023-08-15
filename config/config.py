import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv()


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{os.environ.get("SQLALCHEMY_DATABASE_NAME")}'
    SQLALCHEMY_TRACK_MODIFICATIONS = os.environ.get('SQLALCHEMY_TRACK_MODIFICATIONS') == "True"
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')
