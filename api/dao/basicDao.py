from flask import current_app
from sqlalchemy.exc import SQLAlchemyError

from database import db

class BasicDao:
    @staticmethod
    def safe_commit() -> bool:
        try:
            db.session.commit()
            current_app.logger.info("SQL Safely Committed")
            return True
        
        except SQLAlchemyError as error:

            db.session.rollback()
            current_app.logger.error("SQL Commit Failed!  Rolling back...")
            current_app.logger.error(error.args)
            return False