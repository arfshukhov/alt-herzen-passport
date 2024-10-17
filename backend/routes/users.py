import json
from pprint import pprint

from flask import jsonify

from ..middleware.users_middleware import (
    UserWriter, UsersList, UserReader
)
from ..origin import (
    app, request
)
from ..settings import ServerSettings


@app.route(f"{ServerSettings.API_PATH}/users", methods=["post"])
def create_user():
    email = request.json.get("email")
    password = request.json.get("password")
    name = request.json.get("full_name")
    is_superuser = request.json.get("is_superuser")
    is_active = request.json.get("is_active")
    new_user = list(UserWriter(email=email,
                                password=password,
                                full_name=name,
                                is_superuser=is_superuser,
                                is_active=is_active).write()
                    )
    match new_user[1]:
        case 200:
            return jsonify(new_user[0]), 200
        case 422:
            return jsonify(new_user[0]), 422
        case 409:
            return jsonify({"msg": "conflict"}), 409

@app.route(f"{ServerSettings.API_PATH}/users/", methods=["get"])
def get_users():
    try:
        skip = int(request.json.get("skip"))
        limit = int(request.json.get("limit"))
        users = UsersList(skip=skip, limit=limit).get
        res = {
            "data": list(users),
            "count": len(users)
        }
        return jsonify(res), 200
    except Exception:
        return jsonify({
                "detail": [
                    {
                        "loc": [
                            "string",
                            0
                        ],
                        "msg": "invalid data",
                        "type": "string"
                    }
                ]
        }), 422

@app.route(ServerSettings.API_PATH+"/users/<int:user_id>", methods=["get"])
def get_user(user_id):
    try:

        user = UserReader(_id=user_id).get
        res = dict(user)
        return jsonify(res), 200
    except Exception:
        return jsonify({
                "detail": [
                    {
                        "loc": [
                            "string",
                            0
                        ],
                        "msg": "invalid data",
                        "type": "string"
                    }
                ]
        }), 422


@app.route(ServerSettings.API_PATH+"/users/open", methods=["POST"])
def create_user_open():
    email = request.json.get("email")
    password = request.json.get("password")
    name = request.json.get("full_name")
    new_user = list(UserWriter(email=email,
                                password=password,
                                full_name=name).write()
                    )
    match new_user[1]:
        case 200:
            return jsonify(new_user[0]), 200
        case 422:
            return jsonify(new_user[0]), 422
        case 409:
            return jsonify({"msg": "conflict"}), 409