from flask import request
import jwt
from functools import wraps
from db import Db


SECRET_KEY = "PRML"
MODEL_CONTAINER_URL = "http://arvix_model:30022/api/"


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get("Authorization")
        conn = Db()
        collection = conn.db.users
        if not token:
            return {"message": "Token is missing."}, 401

        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            current_user = collection.find_one({"user_id": data["user_id"]})
        except:
            return {"message": "Token is invalid."}, 401

        return f(current_user, *args, **kwargs)

    return decorated
