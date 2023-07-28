from app.extensions import db
from datetime import datetime, timedelta

class User(db.Model):
   __tablename__ = 'user'
   id = db.Column(db.Integer, primary_key=True)
   full_name = db.Column(db.String(50))
   email = db.Column(db.String(50))
   password = db.Column(db.String(50))
   date_registered = db.Column(db.DateTime, default = datetime.utcnow())
   admin = db.Column(db.Boolean)