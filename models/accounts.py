# TODO

# 6. Пройтись по одному роуту, перглянути, що можна винести в методи моделей

# 7. Покрити тестами нові методи моделей
# 8. Пошукати код який повторюється і винести  в окрему функцію у файл helpers або utils

import os
import uuid
from datetime import datetime

from flask import abort, current_app, jsonify, make_response, url_for
from flask_jwt_extended import (create_access_token, create_refresh_token,
                                get_jwt_identity)
from itsdangerous import URLSafeTimedSerializer
from pydantic import ValidationError
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import mapped_column, relationship
from werkzeug.security import check_password_hash, generate_password_hash

from config import Config
from dependencies import db
from utils.utils import serialize

PROFILE_PHOTOS_PATH = os.path.join(Config.MEDIA_PATH, 'profile')


class User(db.Model):
    __tablename__ = "users"

    id = mapped_column(Integer, primary_key=True)
    full_name = mapped_column(String)
    email = mapped_column(String)
    joined_at = mapped_column(DateTime, default=datetime.utcnow())
    is_active = mapped_column(Boolean, default=False)
    profile_picture = mapped_column(String)
    phone_number = mapped_column(String, default=None)

    shops = relationship("Shop", back_populates="owner")
    delivery_user_info = relationship("DeliveryUserInfo",
                                                                        back_populates="owner")
    comment = relationship("ProductComment", back_populates="user_comment")

    def __init__(self, email, full_name):
        self.email = email
        self.full_name = full_name

    @classmethod
    def get_user_id(cls):
        current_user_id = get_jwt_identity()
        return User.query.filter_by(id=current_user_id).first()
    
    @classmethod
    def create_user(cls, email, full_name, password):
        user = cls(email=email, full_name=full_name)
        db.session.add(user)
        db.session.flush()
        Security.create_security(user.id, password=password)
        return user
    
    def generate_verification_token(self):
        serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        token = serializer.dumps(self.email, salt='email-verification')
        verification_link = url_for('accounts.verify_email', token=token, _external=True)
        return verification_link
    
    @classmethod
    def sign_in(cls, email, password):
        user = cls.query.filter_by(email=email).first()
        
        if user is None or not check_password_hash(
        Security.query.filter_by(user_id=user.id).first().password_hash, password):
            abort(400, "Incorrect password")

        access_token = create_access_token(identity=user.id, fresh=True)
        refresh_token = create_refresh_token(user.id)
        response = {"access_token": access_token, "refresh_token": refresh_token}
        return response
    
    def user_phone_number_change(phone_number):
        user_id = get_jwt_identity()
        user = User.query.filter_by(id=user_id).first()
        if user:
            try:
                user.phone_number = phone_number
                db.session.commit()
                return jsonify({'message': 'Phone number updated successfully'}), 200
            except ValueError as e:
                return jsonify({'error': str(e)}), 400
        return jsonify({'error': 'User not found'}), 404
    
    def user_full_name_change(full_name):
        user_id = get_jwt_identity()
        user = User.query.filter_by(id=user_id).first()

        if user:
            try:
                user.full_name = full_name
                db.session.commit()
                return jsonify({'message': 'Full name updated successfully'}), 200
            except ValidationError as e:
                return jsonify({"error": str(e)}), 400
        return jsonify({'error': 'User not found'}), 404
    
    @classmethod
    def user_full_info(cls):
        user = User.query.filter_by(id=get_jwt_identity()).first()
        delivery_info = DeliveryUserInfo.get_delivery_info_by_owner_id(user.id)
        user_full_data = serialize(user)
        delivery_info_data = serialize(delivery_info)
        if user_full_data["profile_picture"] is not None:

            profile_picture_path = url_for('static', filename=f'media/'
                                        f'profile/{user_full_data["profile_picture"]}',
                                        _external=True)
            user_full_data['profile_picture'] = profile_picture_path
        user_full_info = {**user_full_data, **delivery_info_data}
        return user_full_info
    @classmethod
    def user_profile_photo_get(cls):
        user = User.get_user_id()
        if user.profile_picture is not None:
            filename = user.profile_picture
            return url_for('static', filename=f'media/profile/{filename}', _external=True)
        return make_response('Profile_photo not allowed', 404)
    
    @classmethod
    def user_profile_photo_update(cls, request):
        file = request.files['image']
        _ , file_extension = os.path.splitext(file.filename)
        user = User.get_user_id()
        file_name = uuid.uuid4().hex
        user = User.query.filter_by(id=get_jwt_identity()).first()

        if user.profile_picture is not None:
            prev_photo = os.path.join(PROFILE_PHOTOS_PATH, user.profile_picture)
            if os.path.isfile(prev_photo):
                os.remove(prev_photo)

        user.profile_picture = file_name + file_extension
        file.save(os.path.join(PROFILE_PHOTOS_PATH, file_name + file_extension))
        db.session.commit()
        filename = user.profile_picture
        return url_for('static', filename=f'media/profile/{filename}', _external=True)
    
    
    @classmethod
    def user_profile_photo_delete(cls):
        user = User.get_user_id()
        file = os.path.join(PROFILE_PHOTOS_PATH, user.profile_picture)
        if os.path.isfile(file):
            os.remove(file)
        user.profile_picture = None
        db.session.commit()
        return make_response('OK', 200)
    
    @classmethod
    def user_change_password(cls, user_data):
        user = User.get_user_id()
        security = Security.query.filter_by(user_id=user.id).first()
        if user and security:
            if check_password_hash(security.password_hash, user_data.current_password):
                hashed_password = generate_password_hash(user_data.new_password)
                security.password_hash = hashed_password
                db.session.commit()
                return jsonify({'message': 'Password updated successfully'}), 200
        return jsonify({'error': 'Current password is incorrect'}), 400

    
    @classmethod
    def verify_user_email(cls, token):
        serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])

        try:
            email = serializer.loads(token, salt='email-verification', max_age=3600)
            user = User.query.filter_by(email=email).first()
            user.is_active = True
            db.session.commit()
            return make_response(jsonify({"message": "OK"}), 200)
        except Exception:
            abort(404, "Invalid verification token")
    



class Security(db.Model):
    __tablename__ = "security"

    user_id = mapped_column(Integer, ForeignKey("users.id"), primary_key=True)
    password_hash = mapped_column(String(64))

    def __init__(self,user_id, password):
        self.user_id = user_id
        self.password_hash = password

    @classmethod
    def create_security(cls,user_id, password):
        security = cls(user_id=user_id, password=generate_password_hash(password))
        db.session.add(security)
        db.session.commit()
        return security

class DeliveryUserInfo(db.Model):
    __tablename__ = "delivery_user_info"

    id = mapped_column(Integer, primary_key=True)
    owner_id = mapped_column(Integer, ForeignKey("users.id"))
    post = mapped_column(String, default=None)
    city = mapped_column(String, default=None)
    branch_name = mapped_column(String, default=None)
    address = mapped_column(String, default=None)

    owner = relationship("User", back_populates="delivery_user_info")

    def __init__(self, owner_id, **kwargs):
        self.owner_id = owner_id
        self.post = kwargs.get('post')
        self.city = kwargs.get('city')
        self.branch_name = kwargs.get('branch_name')
        self.address = kwargs.get('address')

    @classmethod
    def get_delivery_info_by_owner_id(cls, owner_id):
        return cls.query.filter_by(owner_id=owner_id).first()

    @classmethod
    def add_delivery_info(cls, **kwargs):
        user = User.get_user_id()
        existing_delivery = DeliveryUserInfo.get_delivery_info_by_owner_id(user.id)
        if not existing_delivery:
            new_delivery_address = cls(owner_id=user.id, **kwargs)
            db.session.add(new_delivery_address)
            db.session.commit()
            return jsonify({'message': 'Delivery address created successfully'}), 201

        existing_delivery.update_delivery_info(**kwargs)
        return jsonify({'message': 'Delivery address updated successfully'}), 200

    
    def update_delivery_info(self,**data):
        if data['post']:
            self.post = data['post']
        if data['city']:
            self.city = data['city']
        if data['branch_name']:
            self.branch_name = data['branch_name']
        if data['address']:
            self.address = data['address']
        db.session.commit()

    @classmethod
    def remove_delivery_info(cls):
        user = User.get_user_id()
        existing_delivery = DeliveryUserInfo.get_delivery_info_by_owner_id(user.id)
        if existing_delivery:
            db.session.delete(existing_delivery)
            db.session.commit()
            return jsonify({'message': 'Delivery address removed successfully'}), 200
        return jsonify({'message': 'User not found'})