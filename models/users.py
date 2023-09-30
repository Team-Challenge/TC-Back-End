from datetime import datetime
from app import db, ma
from marshmallow import fields, Schema, validate


class User(db.Model):
    __tablename__ = "users"

    def __init__(self, email, full_name):
        self.email = email
        self.full_name = full_name

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(50))
    email = db.Column(db.String(50))
    joined_at = db.Column(db.DateTime, default=datetime.utcnow())
    is_active = db.Column(db.Boolean, default=False)
    phone_number = db.Column(db.String(15), default=None)


class Security(db.Model):
    __tablename__ = "security"

    def __init__(self, password):
        self.password_hash = password

    user_id = db.Column(db.Integer, db.ForeignKey(
        "users.id"), primary_key=True)
    password_hash = db.Column(db.String(64))


class UserSchema(ma.SQLAlchemyAutoSchema):
    email = fields.Email()
    class Meta:
        model = User


class SignupUserSchema(Schema):
    email = fields.Email()
    full_name = fields.Str(validate=validate.Length(min=2, max=50))
    password = fields.Str(validate=validate.Length(min=8))


class SigninUserSchema(Schema):
    email = fields.Email()
    password = fields.Str()

class UserUpdateSchema(Schema):
    full_name = fields.Str(validate=validate.Length(min=2, max=50))
    phone_number = fields.Str()