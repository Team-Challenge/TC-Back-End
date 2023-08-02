from models import User
from database import db_session

class UserDao:

    @staticmethod
    def add_user(user: User) -> bool:
        db_session.add(user)
        return db_session.commit()
    
    @staticmethod
    def get_user_by_email(email: str) -> User:
        return db_session.query(User).filter_by(email = email).first()
    
    @staticmethod
    def get_user_by_id(id: int) -> User:
        return db_session.query(User).filter_by(id = id).first()
    
    @staticmethod
    def login(email: str, password: str) -> User:
        user = UserDao.get_user_by_email(email)
        if user.password == password:
            return User