# pylint: skip-file

import json
import logging
import os.path
import sys
from pathlib import Path

sys.path.append('.')

from werkzeug.security import generate_password_hash

from app import create_app, db
from models.accounts import Security, User
from models.patterns import SubCategoryEnumDict, get_subcategory
from models.products import Categories, Product
from models.shops import Shop

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


def create_fixture_t(db=db):
    # Load users data from JSON file
    with open(os.path.join(cur_dir, "users_fixture.json")) as users_f:
        users = json.loads(users_f.read())

    # Load categories data from JSON file
    with open(os.path.join(cur_dir.parent, "static/categories/categories.json"), encoding="utf-8") as categories_f:
        categories = json.loads(categories_f.read())

    user_records = []
    security_records = []

    # Get the ID of the last user record, or set it to 0 if no records exist
    try:
        last_record = int(db.session.query(User).order_by(User.id.desc()).first().id)
    except AttributeError:
        last_record = 0

    # Process each user from users_fixture.json
    for user in users:
        user_record = User(user.get("email"), user.get("full_name"))
        security_record = Security(generate_password_hash(user.get("password")))

        user_records.append(user_record)
        last_record += 1
        security_record.user_id = last_record
        security_records.append(security_record)

    # Bulk insert user and security records
    db.session.bulk_save_objects(user_records)
    db.session.bulk_save_objects(security_records)

    category_records = []
    cat_labels = [cat_label.get("label") for cat_label in categories]

    # Check if all categories exist in the database
    query = db.session.query(Categories).filter(Categories.category_name.in_(cat_labels))
    if query.count() < len(cat_labels):
        # Insert missing categories
        for label in cat_labels:
            category_record = Categories(category_name=label)
            category_records.append(category_record)
        db.session.bulk_save_objects(category_records)

    products_records = []

    # Create shop record
    shop = Shop(owner_id=1, name="Test Name", description="Test Description", phone_number="+380996993333")
    db.session.add(shop)
    db.session.commit()

    # Get the ID of the last product record, or set it to 0 if no records exist
    try:
        last_product = db.session.query(Product.id).order_by(Product.id.desc()).first().id
    except AttributeError:
        last_product = 0

    # Process categories and subcategories to create products
    # # This loop creates product for each subcategory, in total - 21
    # # # Product will be created with CategoryName_SubCatName_SubCatId_LastProductID as product_name
    for i in range(0, len(categories)):
        cat_id = categories[i].get("id")
        filtered_dict = {key: value for key, value in SubCategoryEnumDict.items() if str(key).startswith(str(cat_id))}
        for subcat in filtered_dict:
            last_product += 1
            subcat_name = get_subcategory(subcat)
            product_record = Product(product_name=f"{categories[i].get('label')}_{subcat_name}_{subcat}_{last_product}",
                                     product_decsription="Test Description_" + str(last_product),
                                     category_id=cat_id, sub_category_name=subcat_name, shop_id=shop.id)
            products_records.append(product_record)

    # Bulk insert product records
    db.session.bulk_save_objects(products_records)
    db.session.commit()


if __name__ == "__main__":
    app = create_app()
    # create_fixtures()

    with app.app_context():
        create_fixture_t()
