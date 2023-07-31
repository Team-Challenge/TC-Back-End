from database import db
from datetime import datetime, timedelta

class User(db.Model):

   def __init__(self, user: dict):
      self.email = user.get("email")
      self.full_name = user.get("full_name")
      self.password = user.get("password")

   __tablename__ = 'users'

   id = db.Column(db.Integer, primary_key=True)
   full_name = db.Column(db.String(50))
   email = db.Column(db.String(50))
   password = db.Column(db.String(50))
   date_registered = db.Column(db.DateTime, default = datetime.utcnow())
   admin = db.Column(db.Boolean)