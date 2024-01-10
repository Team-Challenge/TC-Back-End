# pylint: skip-file

import json
import sys
import logging

sys.path.append('.')

from werkzeug.security import generate_password_hash
from app import create_app, db
from models.models import User, Security




def create_fixtures():

    with open("data/users_fixture.json") as f:
        users = json.loads(f.read())
        with app.app_context():
            for user in users:
                user_record = User(user["email"], user["full_name"])
                security_record = Security(generate_password_hash(user["password"]))

                db.session.add(user_record)
                db.session.flush()

                security_record.user_id = user_record.id
                db.session.add(security_record)
                db.session.commit()
    logging.info("Users fixtures have been created.")

if __name__ == "__main__":
    app = create_app()
    create_fixtures()
