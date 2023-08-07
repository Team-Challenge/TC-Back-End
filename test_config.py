import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv()

class Config:
    SECRET_KEY = "fds"
    SQLALCHEMY_DATABASE_URI = "sqlite:////home/kyrylo/TC-Back-End/test_market.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = "super-secret"