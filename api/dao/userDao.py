from model.user import User
from dao.basicDao import BasicDao
from database import db

class UserDao:

    @staticmethod
    def add_user(user: User) -> bool:
        db.session.add(user)
        return BasicDao.safe_commit()
    
    @staticmethod
    def get_user_by_email(email: str) -> User:
        return User.query \
            .filter_by(email = email) \
            .first()