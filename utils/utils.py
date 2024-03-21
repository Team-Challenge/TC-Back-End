import json
import os
import uuid
from os import SEEK_END

from flask import url_for
from werkzeug.datastructures import FileStorage

from config import Config
from models.errors import FileTooLargeError, BadFileTypeError, NoImageError
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


def load_and_save_image(image_field, photo: FileStorage, photo_path):
    """
        Load and save images.

        Parameters:
            image_field: Model field for image.

            photo: The werkzeug FileStorage item from [request.files] to be saved.

            photo_path (str): Absolute path to save (EX: PROFILE_PHOTOS_PATH).


        Raises:
            FileTooLargeException: If the size of the image exceeds the maximum allowed size.
    """

    if not photo:
        raise NoImageError("No image provided")

    banner_shop_path = os.path.join(Config.MEDIA_PATH, 'banner_shops')
    if photo_path == banner_shop_path:
        max_file_size = 5242880
    else:
        max_file_size = 3145728
    file_size = photo.seek(0, SEEK_END)
    if file_size > max_file_size:
        raise FileTooLargeError(
            f"File size too large. Maximum file size is {round(max_file_size / 1048576)}MB.")
    # Return cursor to 0. Without seek(0) file will be broken.
    photo.seek(0)

    file_type, file_extension = photo.content_type.split("/")
    if file_type != "image" or file_extension not in ('png', 'jpg', 'jpeg', 'webp'):
        raise BadFileTypeError("Bad request. Does file have proper file format?")

    file_name = uuid.uuid4().hex
    file_path = os.path.join(
        photo_path, f"{file_name}.{file_extension}")
    if image_field:
        old_file_path = os.path.join(photo_path, image_field)
        if os.path.isfile(old_file_path):
            os.remove(old_file_path)
    image_path = f"{file_name}.{file_extension}"
    photo.save(file_path)
    return image_path
