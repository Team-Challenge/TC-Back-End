import datetime
import os
import sys

from dotenv import load_dotenv
from google_auth_oauthlib.flow import Flow

load_dotenv()
basedir = os.path.abspath('.')


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    __db_name = os.environ.get('SQLALCHEMY_DB_NAME')
    if not __db_name or __db_name == '':
        sys.stdout.write("SQLALCHEMY_DB_NAME env variable not provided!\n")
        sys.exit(1)
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'data', __db_name)
    SQLALCHEMY_TRACK_MODIFICATIONS = os.environ.get('SQLALCHEMY_TRACK_MODIFICATIONS',
                                                    'False') == "True" 
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'Secret')
    MEDIA_PATH = os.path.join(basedir, 'static', 'media')
    __jwt_access_token_expires = os.environ.get('JWT_ACCESS_TOKEN_EXPIRES')
    JWT_ACCESS_TOKEN_EXPIRES = (
        datetime.timedelta(seconds=int(__jwt_access_token_expires))
        if __jwt_access_token_expires
        else None
    )

    FLOW = Flow.from_client_config({'web': {
        'client_id': os.getenv("GOOGLE_CLIENT_ID"),
        'project_id': os.getenv("GOOGLE_PROJECT_ID"),
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        'client_secret': os.getenv("GOOGLE_CLIENT_SECRET"),
        'javascript_origins': [
            "http://localhost:8000",
            "https://fe-marketplace-nvlri.ondigitalocean.app",
            "http://localhost:8080",
            "http://127.0.0.1:8080",
            "https://api.dorechi.store"
        ]}},
        scopes=[
                "https://www.googleapis.com/auth/userinfo.profile",
                "https://www.googleapis.com/auth/userinfo.email",
                "openid",
            ],
        redirect_uri='http://localhost:8000'
        )


class TestConfig:
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get('SECRET_KEY')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')
