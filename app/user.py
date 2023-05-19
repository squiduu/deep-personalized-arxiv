import datetime

import jwt
import requests
from db import Db
from flask import jsonify, request
from flask_restx import Namespace, Resource
from utils import MODEL_CONTAINER_URL, SECRET_KEY

User = Namespace("User")


@User.route("/login")
class Login(Resource):
    """The Login View"""

    def __init__(self):
        conn = Db()
        self.collection = conn.db.users

    def post(self):
        user_id = request.json["user_id"]
        password = request.json["password"]

        user_info = self.collection.find_one({"user_id": user_id})

        if user_info is None:
            return {"message": "Invalid username or password."}, 401

        id_val = user_info["user_id"]
        pw_val = user_info["password"]

        if user_id == id_val and password == pw_val:
            token = jwt.encode(
                {
                    "user_id": user_id,
                    "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=2),
                },
                SECRET_KEY,
                algorithm="HS256",
            )

            return jsonify({"token": token})

        else:
            return {"message": "Invalid username or password."}, 401


@User.route("/register")
class Register(Resource):
    def __init__(self):
        conn = Db()
        self.collection = conn.db.users

    def post(self):
        user_id = request.form["user_id"]
        password = request.form["password"]

        centroid_url = MODEL_CONTAINER_URL + "create_centroid"
        centroid = requests.get(centroid_url)

        if self.collection.find_one({"user_id": user_id}):
            return {"message": "Already exsiting user."}, 401

        else:
            user_data = {"user_id": user_id, "password": password, "centroid": centroid}

            self.collection.insert_one(user_data)

            return {"message": "User registered successfully."}, 201
