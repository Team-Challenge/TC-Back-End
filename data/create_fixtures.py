# pylint: skip-file

import json
import logging
import os.path
import random
import sys
from io import BytesIO
from pathlib import Path
from unittest.mock import patch

sys.path.append('.')

from werkzeug.security import generate_password_hash
from werkzeug.datastructures import FileStorage

from app import create_app, db
from models.accounts import Security, User
from models.products import Categories, Product, ProductDetail, ProductPhoto
from models.shops import Shop
from validation.products import get_subcategory_name

cur_dir = Path(__file__).resolve().parent


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


def create_fixture_t():
    cat_labels = ["На голову", "На вуха", "На шию", "На руки", "Аксесуари", "Набори"]
    sub_categories = [
        [11, 12, 13, 14],
        [21, 22],
        [31, 32, 33, 34, 35, 36, 37, 38, 39],
        [41, 42],
        [51, 52, 53],
        [61],
    ]

    # Load users data from JSON file
    with open(os.path.join(cur_dir, "users_fixture.json")) as users_f:
        users = json.loads(users_f.read())

    # Get the ID of the last user record, or set it to 0 if no records exist
    try:
        last_record = int(db.session.query(User).order_by(User.id.desc()).first().id) + 1
    except AttributeError:
        last_record = 0

    user_records = []
    security_records = []
    # Process each user from users_fixture.json
    for user in users:
        user_record = User(f"{user.get('email')}", user.get("full_name"))
        security_record = Security(user_id=user_record.id,
                                   password=generate_password_hash(user.get("password")))

        user_records.append(user_record)
        last_record += 1
        security_record.user_id = last_record
        security_records.append(security_record)

    # Bulk insert user and security records
    db.session.bulk_save_objects(user_records)
    db.session.bulk_save_objects(security_records)

    # Check if all categories exist in the database
    query = db.session.query(Categories).filter(Categories.category_name.in_(cat_labels))
    first_user = User.query.first()
    category_records = []
    if query.count() < len(cat_labels):
        # Insert missing categories
        for label in cat_labels:
            category_record = Categories(category_name=label)
            category_records.append(category_record)
        db.session.bulk_save_objects(category_records)

    # Create shop record
    shop = Shop.query.get(1)
    if not shop:
        shop = Shop(owner_id=first_user.id, name="Beatles_fixture",
                    description="Beatles_description_fixture",
                    phone_number="+380996993333")
        db.session.add(shop)
        db.session.commit()

    # Get the ID of the last product record, or set it to 0 if no records exist
    try:
        last_product = db.session.query(Product.id).order_by(Product.id.desc()).first().id
    except AttributeError:
        last_product = 0

    # Process categories and subcategories to create products
    # # This loop creates product for each subcategory, in total - 21
    # # # Product will be created with CategoryName_SubCatName_SubCatId_LastProductID
    # # #as product_name
    for i in range(0, len(cat_labels)):
        cat_id = i + 1
        for sub_cat_id in sub_categories[i]:
            last_product += 1
            subcat_name = get_subcategory_name(cat_id, sub_cat_id)

            Product.add_product(
                price=1,
                user_id=shop.owner_id,
                product_name=f"{cat_labels[i]}_{sub_cat_id}_{subcat_name}_{last_product}",
                product_decsription="Test Description_" + str(
                    last_product),
                category_id=cat_id, sub_category_id=sub_cat_id,
            )
            photo = FileStorage(
                stream=BytesIO(b'file_mock'),
                filename='example.jpg',
                content_type='image/jpeg'
            )
            with patch("werkzeug.datastructures.file_storage.FileStorage.save"):
                ProductPhoto.add_product_photo(user_id=shop.owner_id,
                                               product_id=last_product,
                                               photo=photo, main=True)

    # Bulk insert product records
    db.session.commit()


if __name__ == "__main__":
    app = create_app()
    # create_fixtures()

    with app.app_context():
        create_fixture_t()
