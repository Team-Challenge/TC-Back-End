from flask import Blueprint
from flask_restx import Api

bp = Blueprint('auth', __name__)
api = Api(bp)

from app.auth import routes