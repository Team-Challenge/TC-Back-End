
import os

from flask import Blueprint, current_app, send_from_directory, make_response, jsonify
from flask_cors import CORS


orders_route = Blueprint("orders_route", __name__, url_prefix="/orders")


CORS(orders_route, supports_credentials=True)


@orders_route.route("/nova_post", methods=["GET"])
def get_nova_post_json():
    static_dir = os.path.join(current_app.root_path, 'static')
    try:
        return send_from_directory(static_dir, 'delivery/nova_post.json', as_attachment=True)
    except Exception:
        error_message = {'error': 'File not found in the specified location'}
        return make_response(jsonify(error_message), 404)

@orders_route.route("/ukr_post", methods=["GET"])
def get_ukr_post_json():
    static_dir = os.path.join(current_app.root_path, 'static')
    try:
        return send_from_directory(static_dir, 'delivery/ukr_post.json', as_attachment=True)
    except Exception:
        error_message = {'error': 'File not found in the specified location'}
        return make_response(jsonify(error_message), 404)