from app import db
from flask import Flask, jsonify, make_response, request, Blueprint
from werkzeug.security import generate_password_hash,check_password_hash
from flask_sqlalchemy import SQLAlchemy
from functools import wraps
from flask_migrate import Migrate
import uuid
import jwt
from datetime import datetime, timedelta
import sqlite3
from dao.userDao import UserDao
from config import Config

signin_route = Blueprint("signin_route", __name__, url_prefix="/signin")

@signin_route.route('/signin')
def signin(self):
    data = request.get_json()
    try:
        user = UserDao.get_user_by_email(data['email'])
        if user and check_password_hash(user.password, data['password']) == True:
            return encode_token(user.id)
        else:
            return False
    except Exception as e:
        return False


def encode_token(user_id):
    payload ={
        'exp': datetime.utcnow() + timedelta(days=1),
        'iat' :datetime.utcnow(),
        'sub':user_id
    }
    token = jwt.encode(payload, Config.SECRET_KEY, algorithm= 'HS256')
    return token


'''@api.route('/protected', methods=['GET'])
@token_required 
def protected():  
   return "protected zone"'''
