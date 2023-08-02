import uuid
from datetime import datetime, timedelta
from sqlalchemy import Column, Integer, String, Boolean, DateTime, UUID
from sqlalchemy.ext.declarative import declarative_base
from werkzeug.security import generate_password_hash, check_password_hash
Base = declarative_base()
metadata = Base.metadata

class User(Base):

   __tablename__ = 'users'

   def __init__(self, user: dict):
      self.email = user.get("email")
      self.full_name = user.get("full_name")
      self.password_hash = generate_password_hash(user.get("password"))

   id = Column(Integer, primary_key=True)
   full_name = Column(String(50))
   email = Column(String(50))
   password_hash = Column(String(50))
   joined_at = Column(DateTime, default = datetime.utcnow())

   def set_password(self, password):
      self.password_hash = generate_password_hash(password)

   def check_password(self,password):
      return check_password_hash(self.password_hash,password)