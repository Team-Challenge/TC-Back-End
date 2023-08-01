from datetime import datetime, timedelta
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()
metadata = Base.metadata

class User(Base):

   def __init__(self, user: dict):
      self.email = user.get("email")
      self.full_name = user.get("full_name")
      self.password = user.get("password")

   __tablename__ = 'users'

   id = Column(Integer, primary_key=True)
   full_name = Column(String(50))
   email = Column(String(50))
   password = Column(String(50))
   date_registered = Column(DateTime, default = datetime.utcnow())
   admin = Column(Boolean)