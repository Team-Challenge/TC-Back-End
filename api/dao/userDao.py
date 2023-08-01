from models import User
#from dao.basicDao import BasicDao
from database import db_session

class UserDao:

    @staticmethod
    def add_user(user: User) -> bool:
        db_session.add(user)
        return db_session.commit()
    
    @staticmethod
    def get_user_by_email(email: str) -> User:
        return db_session.query(User).filter_by(email=email).first()