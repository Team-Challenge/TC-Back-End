
from flask import jsonify, Blueprint
from marshmallow import ValidationError

error_handlers = Blueprint("error_handlers", __name__)

class APIError(Exception):
    pass


class APIAuthError(APIError):
    code = 403
    description = "Authentication Error"


@error_handlers.app_errorhandler(APIAuthError)
def handle_exception(err):
    response = {"error": err.description, "message": ""}
    return jsonify(response), err.code

@error_handlers.app_errorhandler(ValidationError)
def handle_exceptiosn(err):
    response = {"error": "Invalid input"}
    return jsonify(response), 400
