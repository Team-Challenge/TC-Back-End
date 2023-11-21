from flask import Blueprint
from models.models import Order
from models.schemas import OrderSchema
from flask_cors import CORS


orders_route = Blueprint("orders_route", __name__, url_prefix="/orders")


CORS(orders_route, supports_credentials=True)

@orders_route.route("/all", methods=["GET"])
def get_all_orders():
    a = Order.query.filter_by(user_id=1).first()
    return OrderSchema().dump(a)