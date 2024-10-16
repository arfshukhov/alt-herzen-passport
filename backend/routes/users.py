import json

from flask import jsonify

from backend.middleware.users_middleware import UserWriter
from backend.origin import app, request
from backend.settings import ServerSettings


@app.route(f"{ServerSettings.API_PATH}/users", methods=["post"])
def create_user():
    email = request.json.get("email")
    password = request.json.get("password")
    name = request.json.get("full_name")
    new_user = json.loads(
        str(UserWriter(email=email, password=password, full_name=name))
    )
    match new_user[1]:
        case 200:
            return jsonify(new_user[0]), 200
        case 422:
            return jsonify(new_user[0]), 422
        case 409:
            return jsonify({"msg": "Conflict"}), 409
