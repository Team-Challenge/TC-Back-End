class ServerResponse:
    """
    A class representing server responses for various scenarios.
    Returns tuple[dict, int]
    Example:
        {"message": 'OK'}, 200
    """
    OK = {"message": 'OK'}, 200
    BAD_REQUEST = {"error": "Invalid request data"}, 400
    EMPTY_DATA = {"error": "Empty request data"}, 400
    METHOD_NOT_ALLOWED = {"error": "Method Not Allowed"}, 405
    TOKEN_EXPIRED = {"error": "Verification token expired"}, 400
    INVALID_TOKEN = {"error": "Invalid verification token"}, 400
    NO_FILE_PROVIDED = {'error': 'No file provided'}, 400
    # User responses:
    USER_NOT_FOUND = {"error": 'User not found'}, 404

    # Shop responses:
    SHOP_CREATED = {'message': 'Shop created successfully'}, 201
    SHOP_UPDATED = {'message': 'Shop updated successfully'}, 200
    PRODUCT_DEACTIVATED = {"message": "Product deactivated"}, 200
    BANNER_NOT_FOUND = {"error": "Banner shop not found"}, 404
    SHOP_NOT_FOUND = {'error': 'Shop not found'}, 404
    PHOTO_SHOP_NOT_FOUND = {"error": 'Photo shop not found'}, 404
<<<<<<< HEAD

    # Products responses
    PRODUCT_CREATED = {'message': 'Product created successfully'}, 201
=======
>>>>>>> UM-197
    # Other responses:
    INTERNAL_SERVER_ERROR = {'error': 'Internal Server Error. Please, contact administrator'}, 500
