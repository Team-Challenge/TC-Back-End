import json
import sys

from werkzeug.security import generate_password_hash

sys.path.append('.')

from app import create_app, db
from models.models import User, Security, Product, Order, ProductOrder


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
    
    with open("data/products_fixtures.json") as f:
        products = json.loads(f.read())
        with app.app_context():
            for product in products:
                product_record = Product(product["name"])
                db.session.add(product_record)
                db.session.commit()

    with app.app_context():
        user_record = Order(1)
        db.session.add(user_record)
        db.session.commit()

        order_record_1 = ProductOrder(1, 1, 1)
        order_record_2 = ProductOrder(1, 2, 1)
        order_record_3 = ProductOrder(1, 3, 1)
        order_record_4 = ProductOrder(1, 4, 1)
        order_record_5 = ProductOrder(1, 5, 1)

        db.session.add(order_record_1)
        db.session.add(order_record_2)
        db.session.add(order_record_3)
        db.session.add(order_record_4)
        db.session.add(order_record_5)

        db.session.commit()


if __name__ == "__main__":
    app = create_app()
    create_fixtures()
