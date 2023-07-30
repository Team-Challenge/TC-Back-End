from app.auth import api
from app import db
from flask import Flask, jsonify, make_response, request
from werkzeug.security import generate_password_hash,check_password_hash
from flask_sqlalchemy import SQLAlchemy
from functools import wraps
from flask_migrate import Migrate
from app.models.user import User
import uuid
import jwt
from datetime import datetime, timedelta
import sqlite3
from flask_restx import Resource, Api, Namespace, fields

ns = Namespace("api")

login_model = ns.model('Login', {
    'email': fields.String,
    'password': fields.String
})

newuser_model = ns.model('NewUser', {
    'full_name': fields.String,
    'email': fields.String,
    'password': fields.String
})

login_response = ns.model('NewUser', {
    'jwt_token': fields.String
})

@ns.route('/auth', endpoint='auth')
class Auth(Resource):

    def post(self):
        user_data = request.get_json()
        print(user_data)
        user = User.query.filter_by(email = user_data['email']).first()
        if not user:
            try: 

                hashed_password = generate_password_hash(user_data['password'])
                user = User(email =user_data['email'], password =hashed_password)
                db.session.add(user)
                db.session.commit()
                resp = {
                    "status":"success",
                    "message":"User successfully registered",
                }
                return resp#make_response(jsonify(resp)),201

            except Exception as e:
                print(e)
                resp = {
                    "status" :"Error",
                    "message" :" Error occured, user registration failed"
                }
                return resp#make_response(jsonify(resp)),401
        else:
            resp = {
                "status":"error",
                "message":"User already exists"
            }
            return resp#make_response(jsonify(resp)),202
    
    @api.response(200, 'Success', login_response)
    def get(self):
        user_data = request.get_json()
        try:
            user = User.query.filter_by(email = user_data['email']).first()
            if user and check_password_hash(user.password, user_data['password']) == True:
                auth_token = encode_token(user.id)
                resp = {
                    "status":"succes",
                    "message" :"OK",
                    'auth_token':auth_token
                }
                return make_response(jsonify(resp)), 200
            else:
                resp ={
                    "status":"Error",
                    "message":"BAD"
                }
                return make_response(jsonify(resp)), 404

        except Exception as e:
            print(e)
            resp = {
                "Status":"error",
                    "Message":"User login failed"
            }
            return make_response(jsonify(resp)), 404

def encode_token(user_id):
    payload ={
        'exp': datetime.utcnow() + timedelta(days=1),
        'iat' :datetime.utcnow(),
        'sub':user_id
    }
    token = jwt.encode(payload,app.config['SECRET_KEY'],algorithm= 'HS256')
    return token

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if "Authorization" in request.headers:
            token = request.headers["Authorization"].split(" ")[1]
            print(token)
        if not token:
            return {
                "message": "Authentication Token is missing",
                "error": "Unauthorized"
            }, 401
        try:
            data = jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])
            current_user = User().get_by_id(data["user_id"])
            if current_user is None:
                return {
                "message": "Invalid Authentication token",
                "error": "Unauthorized"
            }, 401
        except Exception as e:
            return {
                "message": "An error Occured",
                "error": str(e)
            }, 500

        return f(current_user, *args, **kwargs)

    return decorated

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if "Authorization" in request.headers:
            token = request.headers["Authorization"]
            print(token)
        if not token:
            return {
                "message": "Authentication Token is missing",
                "error": "Unauthorized"
            }, 401
        try:
            data=jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])
            current_user=User().get_by_id(data["user_id"])
            if current_user is None:
                return {
                "message": "Invalid Authentication token",
                "error": "Unauthorized"
            }, 401
        except Exception as e:
            return {
                "message": "An error Occured",
                "error": str(e)
            }, 500

        return f(current_user, *args, **kwargs)

    return decorated

'''@api.route('/protected', methods=['GET'])
@token_required 
def protected():  
   return "protected zone"'''
