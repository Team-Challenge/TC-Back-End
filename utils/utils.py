import json

from flask import url_for

from validation.products import get_subcategory_id


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg'}


def serialize(obj):
    if obj is None:
        return {}
    if hasattr(obj, '__dict__'):
        serialized_data = {key: value for key, value in obj.__dict__.items() if not
        key.startswith('_')}
        missing_attrs = set(obj.__dict__.keys()) - set(serialized_data.keys())
        for attr in missing_attrs:
            serialized_data[attr] = None
        return serialized_data
    if hasattr(obj, '__slots__'):
        serialized_data = {attr: getattr(obj, attr) for attr in obj.__slots__}
        missing_attrs = set(obj.__slots__) - set(serialized_data.keys())
        for attr in missing_attrs:
            serialized_data[attr] = None
        return serialized_data
    return {}


# TODO: better replace in models
def serialize_product(**data):
    if data.get('product_characteristic') is not None:
        data['product_characteristic'] = json.dumps(data['product_characteristic'],
                                                    ensure_ascii=False)

    if data.get('delivery_post') is not None:
        data['delivery_post'] = json.dumps(data['delivery_post'], ensure_ascii=False)

    if data.get('method_of_payment') is not None:
        data['method_of_payment'] = json.dumps(data['method_of_payment'], ensure_ascii=False)
    return data


# TODO: better replace in models
def product_info_serialize(products):
    result = []
    unique_product_ids = set()

    for product, product_detail, _product_photo in products:
        if product.id not in unique_product_ids:
            photos = [photo.serialize() for photo in product_detail.product_to_photo]

            try:
                product_characteristics = json.loads(
                    product_detail.product_characteristic) if (
                        product_detail.product_characteristic is not None) else None
            except ValueError as ex:
                raise ValueError("product_characteristics", ex) from ex

            try:
                method_of_payment = json.loads(
                    product_detail.method_of_payment) if (
                        product_detail.method_of_payment is not None) else None
            except ValueError as ex:
                raise ValueError("method_of_payment", ex) from ex

            try:
                delivery_post = json.loads(product_detail.delivery_post) \
                    if product_detail.delivery_post is not None else None
            except ValueError as ex:
                raise ValueError("delivery_post", ex) from ex

            product_data = {
                "id": product.id,
                "category_id": product.category_id,
                "sub_category_id": get_subcategory_id(product.sub_category_name),
                "shop_id": product.shop_id,
                "product_name": product.product_name,
                "product_description": product.product_description,
                "time_added": product.time_added,
                "time_modifeid": product.time_modifeid,
                "is_active": product.is_active,
                "price": product_detail.price,
                "product_status": product_detail.product_status,

                "product_characteristic": product_characteristics,

                "is_return": product_detail.is_return,

                "delivery_post": delivery_post,

                "method_of_payment": method_of_payment,

                "is_unique": product_detail.is_unique,
                "photos": [{
                    "id": photo.get('id'),
                    "product_photo": url_for(
                        'static',
                        filename=f'media/products/{photo.get("product_photo")}',
                        _external=True),
                    "timestamp": photo.get('timestamp'),
                    "main": photo.get('main')
                } for photo in photos]
            }

            result.append(product_data)
            unique_product_ids.add(product.id)

    return result


def product_info_serialize_by_id(product, product_detail, _product_photo):
    photos = [photo.serialize() for photo in product_detail.product_to_photo]

    try:
        product_characteristics = json.loads(
            product_detail.product_characteristic) if (
                product_detail.product_characteristic is not None) else None
    except ValueError as ex:
        raise ValueError("product_characteristics", ex) from ex

    try:
        method_of_payment = json.loads(
            product_detail.method_of_payment) if (
                product_detail.method_of_payment is not None) else None
    except ValueError as ex:
        raise ValueError("method_of_payment", ex) from ex

    try:
        delivery_post = json.loads(product_detail.delivery_post) \
            if product_detail.delivery_post is not None else None
    except ValueError as ex:
        raise ValueError("delivery_post", ex) from ex

    product_data = {
        "id": product.id,
        "category_id": product.category_id,
        "sub_category_id": get_subcategory_id(product.sub_category_name),
        "shop_id": product.shop_id,
        "product_name": product.product_name,
        "product_description": product.product_description,
        "time_added": product.time_added,
        "time_modifeid": product.time_modifeid,
        "is_active": product.is_active,
        "price": product_detail.price,
        "product_status": product_detail.product_status,

        "product_characteristic": product_characteristics,

        "is_return": product_detail.is_return,

        "delivery_post": delivery_post,

        "method_of_payment": method_of_payment,

        "is_unique": product_detail.is_unique,
        "photos": [{
            "id": photo.get('id'),
            "product_photo": url_for(
                'static',
                filename=f'media/products/{photo.get("product_photo")}',
                _external=True),
            "timestamp": photo.get('timestamp'),
            "main": photo.get('main')
        } for photo in photos]
    }

    return product_data
