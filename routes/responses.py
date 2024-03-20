class ServerResponse:
    """
    A class representing server responses for various scenarios.
    Returns tuple[dict, int]
    Example:
        {"message": 'OK'}, 200
    """
    OK = {"message": 'OK'}, 200
    BAD_REQUEST = {"error": "Invalid request data"}, 400

    # User responses:
    USER_NOT_FOUND = {"error": 'User not found'}, 404

    # Shop responses:
    SHOP_CREATED = {'message': 'Shop created successfully'}, 201
    SHOP_UPDATED = {'message': 'Shop updated successfully'}, 200
    BANNER_NOT_FOUND = {"error": "Banner shop not found"}, 404
    SHOP_NOT_FOUND = {'error': 'Shop not found'}, 404
    PHOTO_SHOP_NOT_FOUND = {"error": 'Photo shop not found'}, 404

    # Other responses:
    INTERNAL_SERVER_ERROR = {'error': 'Internal Server Error. Please, contact administrator'}, 500
