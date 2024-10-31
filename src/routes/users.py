
from sqlite3 import IntegrityError

from flask import jsonify
from peewee import DoesNotExist
from werkzeug.routing import ValidationError

from ..middleware.JWT_processor import Token, PasswordManager
from ..middleware.users_middleware import (
    UserWriter, UsersList, UserReader
)
from ..origin import (
    app, request, traceback, cross_origin
)
from ..settings import ServerSettings


@app.route(f"{ServerSettings.API_PATH}/users", methods=["POST"])
@cross_origin()
@Token.token_required
def create_user(*, _email):
    try:
        email = request.json.get("email")
        password = str(request.json.get("password"))
        name = request.json.get("full_name")
        is_superuser = bool(request.json.get("is_superuser"))
        is_active = bool(request.json.get("is_active"))
        new_user = UserWriter(email=email,
                                    password=password,
                                    full_name=name,
                                    is_superuser=is_superuser,
                                    is_active=is_active).write()
        return jsonify(new_user), 200
    except ValidationError as e:
        return jsonify({
            "detail": [{
                "loc": [
                    f"{e.__class__.__name__}",
                    0
                ],
                "msg": f"{e} {e.__cause__} {e.__doc__} \n "
                       f"{traceback.format_exc()}",
                "type": f"{e.__class__.__name__}"
            }]
        }), 422
    except IntegrityError as e:
        return  jsonify({
            "detail": [{
                "loc": [
                    f"{e.__class__.__name__}",
                    0
                ],
                "msg": f"{e} {e.__cause__} {e.__doc__} \n "
                       f"{traceback.format_exc()}",
                "type": f"{e.__class__.__name__}"
            }]
        }), 409
    except Exception as e:
        return jsonify({
            "detail": [{
                "loc": [
                    f"{e.__class__.__name__}",
                    0
                ],
                "msg": f"{e} {e.__cause__} {e.__doc__} \n "
                       f"{traceback.format_exc()}",
                "type": f"{e.__class__.__name__}"
            }]
        }), 400

@app.route(f"{ServerSettings.API_PATH}/users/", methods=["GET"])
@cross_origin()
@Token.token_required
def get_users(*, _email):
    try:
        skip = int(request.args.get("skip"))
        limit = int(request.args.get("limit"))
        users = UsersList(skip=skip, limit=limit).get
        res = {
            "data": list(users),
            "count": len(users)
        }
        return jsonify(res), 200
    except Exception as e:
        return jsonify({
            "detail": [{
                "loc": [
                    f"{e.__class__.__name__}",
                    0
                ],
                "msg": f"{e} {e.__cause__} {e.__doc__} \n "
                       f"{traceback.format_exc()}",
                "type": f"{e.__class__.__name__}"
            }]
        }), 422

@app.route(ServerSettings.API_PATH+"/users/<int:user_id>", methods=["get"])
@Token.token_required
def get_user(user_id, *, _email):
    try:
        user = UserReader(_id=user_id).get
        res = dict(user)
        return jsonify(res), 200
    except DoesNotExist as e:
        return jsonify({
            "detail": [{
                "loc": [
                    f"{e.__class__.__name__}",
                    0
                ],
                "msg": f"{e} {e.__cause__} {e.__doc__} \n "
                       f"{traceback.format_exc()}",
                "type": f"{e.__class__.__name__}"
            }]
        }), 404
    except Exception as e:
        return jsonify({
            "detail": [{
                "loc": [
                    f"{e.__class__.__name__}",
                    0
                ],
                "msg": f"{e} {e.__cause__} {e.__doc__} \n "
                       f"{traceback.format_exc()}",
                "type": f"{e.__class__.__name__}"
            }]
        }), 422


@app.route(ServerSettings.API_PATH+"/users/open", methods=["POST"])
@cross_origin()
def create_user_open():
    try:
        email = request.args.get("email")
        password = str(request.args.get("   password"))
        name = request.args.get("full_name")
        new_user = UserWriter(email=email,
                                   password=password,
                                   full_name=name
                                   ).write()
        return jsonify(new_user), 200
    except ValidationError as e:
        return jsonify({
            "detail": [{
                "loc": [
                    f"{e.__class__.__name__}",
                    0
                ],
                "msg": f"{e} {e.__cause__} {e.__doc__} \n "
                       f"{traceback.format_exc()}",
                "type": f"{e.__class__.__name__}"
            }]
        }), 422
    except IntegrityError as e:
        return jsonify({
            "detail": [{
                "loc": [
                    f"{e.__class__.__name__}",
                    0
                ],
                "msg": f"{e} {e.__cause__} {e.__doc__} \n "
                       f"{traceback.format_exc()}",
                "type": f"{e.__class__.__name__}"
            }]
        }), 409
    except Exception as e:
        return jsonify({
            "detail": [{
                "loc": [
                    f"{e.__class__.__name__}",
                    0
                ],
                "msg": f"{e} {e.__cause__} {e.__doc__} \n "
                       f"{traceback.format_exc()}",
                "type": f"{e.__class__.__name__}"
            }]
        }), 400


@app.route(ServerSettings.API_PATH+"/users/me", methods=["PATCH"])
@cross_origin()
@Token.token_required
def me_patching(*, _email):

    try:
        email = request.json.get("email")
        full_name = request.json.get("full_name")
        if email != _email:
            raise Exception("its difference between token's email"
                            "and json's email")
        UserWriter.update(email=email, full_name=full_name)
        user = UserReader(email=email).get
        return jsonify(user), 200
    except DoesNotExist as e:
        return jsonify({
            "detail": [{
                "loc": [
                    f"{e.__class__.__name__}",
                    0
                ],
                "msg": f"{e} {e.__cause__} {e.__doc__} \n "
                       f"{traceback.format_exc()}",
                "type": f"{e.__class__.__name__}"
            }]
        }), 404
    except Exception as e:
        return jsonify({
            "detail": [{
                "loc": [
                    f"{e.__class__.__name__}",
                    0
                ],
                "msg": f"{e} {e.__cause__} {e.__doc__} \n "
                       f"{traceback.format_exc()}",
                "type": f"{e.__class__.__name__}"
            }]
        }), 422

@app.route(ServerSettings.API_PATH+"/users/me", methods=["GET"])
@cross_origin()
@Token.token_required
def get_me(*, _email):
    user = UserReader(email=_email).get
    return jsonify(user), 200

@app.route(ServerSettings.API_PATH+"/users/me/password", methods=["PATCH"])
@cross_origin()
@Token.token_required
def change_password(*, _email):
    try:
        current_password = request.json.get("current_password")
        new_password = request.json.get("new_password")
        if PasswordManager.match_password(_email, current_password):
            PasswordManager.update_password(_email, new_password)
            return jsonify({"message": "success"}), 200
        else:
            return jsonify({{
                          "detail": [
                            {
                              "loc": [
                                "password",
                                0
                              ],
                              "msg": "wrong password",
                              "type": "string"
                            }
                          ]
                        }}), 422
    except Exception as e:
        return jsonify({
            "detail": [{
                "loc": [
                    f"{e.__class__.__name__}",
                    0
                ],
                "msg": f"{e} {e.__cause__} {e.__doc__} \n "
                       f"{traceback.format_exc()}",
                "type": f"{e.__class__.__name__}"
            }]
        }), 422


@app.route(ServerSettings.API_PATH+"/users/<int:user_id>", methods=["PATCH"])
@cross_origin()
@Token.token_required
def update_user_by_id(user_id, *, _email):
    try:
        email = request.json.get("email")
        full_name = request.json.get("full_name")
        password = request.json.get("password")
        is_active = request.json.get("is_active")
        is_superuser = request.json.get("is_superuser")
        if email != _email:
            raise Exception("its difference between token's email"
                            "and json's email")
        UserWriter(_id=user_id,
                         email=email,
                         full_name=full_name,
                         is_active=is_active,
                         password=password,
                         is_superuser=is_superuser).update_by_id()
        usr = UserReader(_id=user_id).get
        return jsonify(usr), 200
    except DoesNotExist as e:
        return jsonify({
            "detail": [{
                "loc": [
                    f"{e.__class__.__name__}",
                    0
                ],
                "msg": f"{e} {e.__cause__} {e.__doc__} \n "
                       f"{traceback.format_exc()}",
                "type": f"{e.__class__.__name__}"
            }]
        }), 404
    except Exception as e:
        return jsonify({
            "detail": [{
                "loc": [
                    f"{e.__class__.__name__}",
                    0
                ],
                "msg": f"{e} {e.__cause__} {e.__doc__} \n "
                       f"{traceback.format_exc()}",
                "type": f"{e.__class__.__name__}"
            }]
        }), 422


@app.route(ServerSettings.API_PATH+"/users/<int:user_id>", methods=["DELETE"])
@cross_origin()
@Token.token_required
def delete_user_by_id(user_id, *, _email):
    user_id = request.args.get("user_id")
    try:
        UserWriter.delete_by_id(_id=user_id, email=_email)
        return jsonify({"message": "success"}), 200
    except DoesNotExist as e:
        return jsonify({
            "detail": [{
                "loc": [
                    f"{e.__class__.__name__}",
                    0
                ],
                "msg": f"{e} {e.__cause__} {e.__doc__} \n "
                       f"{traceback.format_exc()}",
                "type": f"{e.__class__.__name__}"
            }]
        }), 404
    except Exception as e:
        return jsonify({
            "detail": [{
                "loc": [
                    f"{e.__class__.__name__}",
                    0
                ],
                "msg": f"{e} {e.__cause__} {e.__doc__} \n "
                       f"{traceback.format_exc()}",
                "type": f"{e.__class__.__name__}"
            }]
        }), 422
