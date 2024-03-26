import datetime
import os
import sys

from dotenv import load_dotenv

from google_auth_oauthlib.flow import Flow

load_dotenv()
_basedir = os.path.abspath('.')
_debug = bool(os.environ.get('DEBUG', 0))


def _get_db_connection_str():
    db_name = os.environ.get('SQLALCHEMY_DB_NAME')
    if not db_name or db_name == '':
        sys.stdout.write("SQLALCHEMY_DB_NAME env variable not provided!\n")
        sys.exit(1)
    return 'sqlite:///' + os.path.join(_basedir, 'data', db_name)

def _init_google_flow():
    redirect_uri = 'http://0.0.0.0:8000' if _debug else 'https://www.dorechi.store'

    return Flow.from_client_config({
        'web': {
        'client_id': os.getenv("GOOGLE_CLIENT_ID"),
        'project_id': os.getenv("GOOGLE_PROJECT_ID"),
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        'client_secret': os.getenv("GOOGLE_CLIENT_SECRET"),
        'javascript_origins': [
            "http://localhost:8000", # local FE url
            "https://www.dorechi.store", # server url
            "https://dorechi.store", # server url
        ]}},
        scopes=["https://www.googleapis.com/auth/userinfo.profile",
                "https://www.googleapis.com/auth/userinfo.email",
                "openid"],
        redirect_uri=redirect_uri
    )


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = _get_db_connection_str()
    SQLALCHEMY_TRACK_MODIFICATIONS = os.environ.get('SQLALCHEMY_TRACK_MODIFICATIONS',
                                                    'False') == "True"
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'Secret')
    MEDIA_PATH = os.path.join(_basedir, 'static', 'media')
    JWT_ACCESS_TOKEN_EXPIRES =  datetime.timedelta(seconds=int(
        os.environ.get('JWT_ACCESS_TOKEN_EXPIRES', '3600')))
    GOOGLE_FLOW = _init_google_flow()


class TestConfig:
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get('SECRET_KEY')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')
    MEDIA_PATH = None
    JWT_ACCESS_TOKEN_EXPIRES =  datetime.timedelta(seconds=3600)
    GOOGLE_FLOW = None
