
from flask import Flask, jsonify, make_response, request, Blueprint, Response, redirect, url_for, abort
from functools import wraps
from datetime import datetime, timedelta
from dao.userDao import UserDao
import jwt
from werkzeug.security import generate_password_hash, check_password_hash

auth_route = Blueprint("auth_route", __name__, url_prefix="/auth")

@auth_route.route('', methods =['POST'])
def login():
    auth = request.get_json()

    user = UserDao.get_user_by_email(auth.get('email'))

    if check_password_hash(user.password, auth.get('password')):

        token = jwt.encode({
            'id': user.id,
            'exp' : datetime.utcnow() + timedelta(minutes = 30)
        }, 'secret')
        return jsonify({'token' : token})