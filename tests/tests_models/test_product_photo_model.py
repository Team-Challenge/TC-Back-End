from io import BytesIO
from unittest.mock import patch

import pytest
from werkzeug.datastructures.file_storage import FileStorage

from models.errors import NotFoundError, BadFileTypeError, ProductPhotoLimitError, NoImageError
from models.products import ProductPhoto
from tests.conftest import create_user_shop_product, TestValidData


def test_add_product_photo_1(session):
    """Test create product scenario success"""
    # Given
    data = create_user_shop_product(session)
    image = TestValidData.get_image()
    photos = []  # noqa

    # When
    with patch("werkzeug.datastructures.file_storage.FileStorage.save") as func:
        photos.append(ProductPhoto.add_product_photo(data.user.id, data.product.id, image, True))
        photos.append(ProductPhoto.add_product_photo(data.user.id, data.product.id, image, False))
        photos.append(ProductPhoto.add_product_photo(data.user.id, data.product.id, image, False))
        photos.append(ProductPhoto.add_product_photo(data.user.id, data.product.id, image, False))

        # Then
        assert func.call_count == 4
        assert len(photos) == 4
        assert photos[0]
        assert photos[0].get("message")
        assert photos[-1].get("message")

    added = ProductPhoto.query.filter_by(product_detail_id=data.detail.id).all()
    assert added[0].id > 0
    assert added[0].product_photo
    assert len(added) == 4

    assert added[0].main is True
    assert added[1].main is False
    assert added[2].main is False
    assert added[3].main is False


def test_add_product_photo_3(session):
    """Test create product scenario negative: ProductPhotoLimitError"""
    # Given
    data = create_user_shop_product(session)
    file_storage = FileStorage(
        stream=BytesIO(b'file_mock'),
        filename='example.jpg',
        content_type='image/jpeg'
    )

    # When
    with pytest.raises(ProductPhotoLimitError):
        with patch("werkzeug.datastructures.file_storage.FileStorage.save") as func:
            ProductPhoto.add_product_photo(data.user.id, data.product.id, file_storage, True)
            ProductPhoto.add_product_photo(data.user.id, data.product.id, file_storage, False)
            ProductPhoto.add_product_photo(data.user.id, data.product.id, file_storage, False)
            ProductPhoto.add_product_photo(data.user.id, data.product.id, file_storage, False)

            ProductPhoto.add_product_photo(data.user.id, data.product.id, file_storage, False)

            # Then
            assert func.call_count == 4

    added = ProductPhoto.query.filter_by(product_detail_id=data.detail.id).all()
    assert added[0].id > 0
    assert added[0].product_photo
    assert len(added) == 4


@pytest.mark.parametrize(
    "user_id, product_id, photo, main, expected_exception, expected_message",
    [
        (9999, 1,
         FileStorage(stream=BytesIO(b'file_mock'), filename='example.jpg',
                     content_type='image/jpeg'), True,
         NotFoundError, "User not found"),
        (1, 9999,
         FileStorage(stream=BytesIO(b'file_mock'), filename='example.jpg',
                     content_type='image/jpeg'), True,
         NotFoundError, "Product not found"),
        (1, 1, '', True, NoImageError, "No image provided"),
        (1, 1, FileStorage(stream=BytesIO(b'file_mock'), filename='example.bmp',
                           content_type='image/bmp'), True,
         BadFileTypeError, "Bad request. Does file have proper file format?")
    ]
)
def test_add_product_photo_negative(session, user_id, product_id, photo, main, expected_exception,
                                    expected_message):
    """Test add product photo scenario with negative conditions"""
    # Given
    create_user_shop_product(session)

    # When
    payload = {
        "user_id": user_id,
        "product_id": product_id,
        "photo": photo,
        "main": main
    }

    # Then
    with pytest.raises(expected_exception, match=expected_message):
        ProductPhoto.add_product_photo(**payload)

    with pytest.raises(expected_exception):
        with patch("werkzeug.datastructures.file_storage.FileStorage.save") as func:
            ProductPhoto.add_product_photo(**payload)
            assert func.call_count == 0

    # Then


def test_get_num_photos(session):
    """Test get photos count for product using detail_id scenario success"""
    # Given
    data = create_user_shop_product(session)

    # When

    # Then
    assert ProductPhoto.get_num_photos_by_product_detail_id(data.detail.id) == 0
