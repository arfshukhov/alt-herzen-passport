import json

from flask import jsonify

from ..middleware.users_middleware import UserWriter
from ..origin import *


@app.route("/users", methods=["post"])
def create_user():
    email = request.json.get("email")
    password = request.json.get("password")
    name = request.json.get("name")
    new_user = json.loads(
        str(UserWriter(email=email, password=password, full_name=name))
    )
    match new_user[1]:
        case 200:
            return jsonify(new_user[1]), 200
        case 422:
            return jsonify(new_user[1]), 422
        case 409:
            return jsonify({"msg": "Conflict"}), 409
