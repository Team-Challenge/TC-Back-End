from flask import jsonify, request, Blueprint, Response, make_response, current_app, url_for, abort

from datetime import datetime, timedelta
from models.models import *
from models.schemas import *
from werkzeug.security import check_password_hash, generate_password_hash
from itsdangerous import URLSafeTimedSerializer
from marshmallow import ValidationError
from flask_cors import CORS
import jwt
import os
import uuid
import json
import phonenumbers
from routes.error_handlers import *
from app import db, jwt
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt_identity,
    get_jwt,
    jwt_required,
    set_access_cookies
)


orders_route = Blueprint("orders_route", __name__, url_prefix="/orders")


CORS(orders_route, supports_credentials=True)

@orders_route.route("/all", methods=["GET"])
def get_all_orders():
    a = Order.query.filter_by(user_id=1).first()
    return OrderSchema().dump(a)