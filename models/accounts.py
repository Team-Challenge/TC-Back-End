# TODO

# 6. Пройтись по одному роуту, перглянути, що можна винести в методи моделей

# 7. Покрити тестами нові методи моделей
# 8. Пошукати код який повторюється і винести  в окрему функцію у файл helpers або utils

import os
import uuid
from datetime import datetime

from flask import url_for
from flask_jwt_extended import (create_access_token, create_refresh_token,
                                get_jwt_identity)
from itsdangerous import BadSignature, SignatureExpired
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import mapped_column, relationship
from werkzeug.security import check_password_hash, generate_password_hash

from config import Config
from dependencies import db
from models.errors import NotFoundError, UserError
from models.shops import Shop
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
    
    # TODO: return success or error message. Remove all flask imports in this file +++++
    # TODO: jsonify should be called in route ++++
    @classmethod
    def sign_in(cls, email, password):
        user = cls.query.filter_by(email=email).first()
        if user:
            if user is None or not check_password_hash(
            Security.query.filter_by(user_id=user.id).first().password_hash, password):
                raise UserError("Incorrect password")

            access_token = create_access_token(identity=user.id, fresh=True)
            refresh_token = create_refresh_token(user.id)
            response = {"access_token": access_token, "refresh_token": refresh_token}
            return response
        raise UserError('User not found')
    
    # TODO: rename: change_number +++++
    # TODO: return success or error message. Remove all flask imports in this file +++++
    # TODO: jsonify should be called in route ++++++
    def change_number(phone_number):
        user = User.get_user_id()
        if user:
            try:
                user.phone_number = phone_number
                db.session.commit()
                response = {'message': 'Phone number updated successfully'}
                return response
            except ValueError as e:
                raise UserError(e) from e
        raise NotFoundError('User not found')
    
    # TODO: rename: change_full_name ++++
    # TODO: return success or error message. Remove all flask imports in this file+++++++
    # TODO: jsonify should be called in route+++
    def change_full_name(full_name):
        user = User.get_user_id()
        if user:
            try:
                user.full_name = full_name
                db.session.commit()
                response = {'message': 'Full name updated successfully'}
                return response
            except ValueError as e:
                raise UserError(e) from e
        raise NotFoundError('User not found')
    
    # TODO: rename: get_user_info+++
    @classmethod
    def get_user_info(cls):
        user = User.get_user_id()
        if user is not None:
            delivery_info = DeliveryUserInfo.get_delivery_info_by_owner_id(user.id)
            user_full_data = serialize(user)
            delivery_info_data = serialize(delivery_info)
            if user_full_data["profile_picture"] is not None:

                profile_picture_path = url_for('static', filename=f'media/'
                                            f'profile/{user_full_data["profile_picture"]}',
                                            _external=True)
                user_full_data['profile_picture'] = profile_picture_path
            user_full_info = {**user_full_data, **delivery_info_data}
            shop = Shop.get_shop_by_owner_id(owner_id=user.id)
            if shop or shop is not None:
                user_full_info['shop_id'] = shop.id
                user_full_info['have_a_shop'] = True
            return user_full_info
        raise NotFoundError('User not found')

    # TODO: combine with change_profile_photo (make 1 function)++++++
    # TODO: return success or error message. Remove all flask imports in this file++++++
    # TODO: jsonify should be called in route++++++++
    @classmethod
    def handle_profile_photo(cls, request, action):
        user = cls.get_user_id()
        
        if user is not None:        
            if action == 'upload':
                file = request.files.get('image')
                if file is not None:
                    _, file_extension = os.path.splitext(file.filename)
                    allowed_extensions = {'png', 'jpg', 'jpeg', 'webp'}
                    if file_extension.lower()[1:] not in allowed_extensions:
                        raise UserError('Invalid file format')
                    file_name = uuid.uuid4().hex

                    if user.profile_picture:
                        prev_photo = os.path.join(PROFILE_PHOTOS_PATH, user.profile_picture)
                        if os.path.isfile(prev_photo):
                            os.remove(prev_photo)

                    user.profile_picture = file_name + file_extension
                    file.save(os.path.join(PROFILE_PHOTOS_PATH, file_name + file_extension))
                    db.session.commit()
                    filename = user.profile_picture
                    return {'message': 'Profile photo uploaded successfully', 'filename': filename}
                raise UserError('Bed request data')
        
            if action == 'delete':
                if user.profile_picture:
                    file_path = os.path.join(PROFILE_PHOTOS_PATH, user.profile_picture)
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                    user.profile_picture = None
                    db.session.commit()
                    return {'message': 'Profile photo deleted successfully'}
                raise NotFoundError('Profile photo not found')
            raise ValueError('Invalid action specified')
        raise NotFoundError('User not found')
    
    # TODO: rename: change_password+++++++
    # TODO: return success or error message. Remove all flask imports in this file++++++++
    # TODO: jsonify should be called in route++++++++
    # TODO: in Security class create_method to change password: change_password()+++++++
    @classmethod
    def change_password(cls, **user_data):
        user = User.get_user_id()
        if user:
            response =Security.change_password(user_id=user.id,
                                      current_password=user_data['current_password'], 
                                      new_password=user_data['new_password'])
            return response
        raise NotFoundError('User not found')

    
    # TODO: rename: verify_email+++++
    # TODO: return success or error message. Remove all flask imports in this file++++
    # TODO: jsonify should be called in route+++++
    @classmethod
    def verify_email(cls, token, serializer):
        try:
            email = serializer.loads(token, salt='email-verification', max_age=3600)
            user = User.query.filter_by(email=email).first()
            if user is None:
                raise UserError("User not found")

            user.is_active = True
            db.session.commit()
            return "OK"
        except SignatureExpired as exc:
            raise exc from exc
        except BadSignature as exc:
            raise exc from exc
        except Exception as exc:
            raise exc from exc 
    



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
    
    @staticmethod
    def change_password(user_id, current_password, new_password):
        security = Security.query.filter_by(user_id=user_id).first()
        if security:
            if check_password_hash(security.password_hash, current_password):
                hashed_password = generate_password_hash(new_password)
                security.password_hash = hashed_password
                db.session.commit()
                return {'message': 'Password updated successfully'}
            raise UserError('Invalid password')
        raise NotFoundError('Password not found')



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

    # TODO: rename -> get_delivery_info
    @classmethod
    def get_delivery_info_by_owner_id(cls, owner_id):
        return cls.query.filter_by(owner_id=owner_id).first()

    # TODO: return success or error message. Remove all flask imports in this file++++++
    # TODO: jsonify should be called in route+++++++
    @classmethod
    def add_delivery_info(cls, **kwargs):
        user = User.get_user_id()
        if user is not None:
            existing_delivery = DeliveryUserInfo.get_delivery_info_by_owner_id(user.id)
            if not existing_delivery:
                new_delivery_address = cls(owner_id=user.id, **kwargs)
                db.session.add(new_delivery_address)
                db.session.commit()
                return {'message': 'Delivery address created successfully'}

            existing_delivery.update_delivery_info(**kwargs)
            return {'message': 'Delivery address updated successfully'}
        raise NotFoundError('User not found')

    
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

    # TODO: return success or error message. Remove all flask imports in this file+++++
    # TODO: jsonify should be called in route+++++++++
    @classmethod
    def remove_delivery_info(cls):
        user = User.get_user_id()
        if user is not None:
            existing_delivery = DeliveryUserInfo.get_delivery_info_by_owner_id(user.id)
            if existing_delivery:
                db.session.delete(existing_delivery)
                db.session.commit()
                return {'message': 'Delivery address removed successfully'}
            raise NotFoundError('Delivery adress not found')
        raise NotFoundError('User not found')
