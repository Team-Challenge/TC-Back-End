from functools import wraps
import jwt
from flask import Flask, jsonify, make_response, request

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if "Authorization" in request.headers:
            token = request.headers["Authorization"]
            print(token)
        if not token:
            return {
                "message": "Authentication Token is missing",
                "error": "Unauthorized"
            }, 401
        try:
            data = jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])
            current_user = User().get_by_id(data["user_id"])
            if current_user is None:
                return {
                "message": "Invalid Authentication token",
                "error": "Unauthorized"
            }, 401
        except Exception as e:
            return {
                "message": "An error Occured",
                "error": str(e)
            }, 500

        return f(current_user, *args, **kwargs)

    return decorated