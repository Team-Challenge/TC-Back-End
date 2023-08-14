from flask import Blueprint
from utils.auth import token_required

test_route = Blueprint("test_route", __name__, url_prefix="/tests")

@test_route.route('', methods =['POST'])
@token_required
def test(current_user):
    return current_user
