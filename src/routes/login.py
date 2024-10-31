from flask import jsonify

from ..middleware import *
from ..middleware.users_middleware import UserReader
from ..origin import app, request
from ..settings import ServerSettings
from ..middleware.JWT_processor import *
from ..origin import *


@app.route(ServerSettings.API_PATH+"/login/access-token", methods=["POST"])
@cross_origin()
def access_token():
    try:
        email = str(request.args.get("email"))
        password = str(request.args.get("password"))
        if PasswordManager.match_password(email, password):
            token = Token(email).get_token
            return jsonify({
                    "access_token": token,
                    "token_type": "bearer"
            }), 200
        else:
            return jsonify({
                    "detail": [
                    {
                      "loc": [
                        "verification data",
                        0
                      ],
                      "msg": "incorrect email or password",
                      "type": "string"
                    }]}), 409
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


@app.route(ServerSettings.API_PATH+"/login/test-token", methods=["POST"])
@cross_origin()
@Token.token_required
def test_token(*, _email):
    user = UserReader(email=_email).get
    return jsonify(user), 200


@app.route(ServerSettings.API_PATH+"/reset-password/", methods=["POST"])
@cross_origin()
def reset_password(*, _email):
    try:
        token = request.json.get("token")
        new_password = str(request.json.get("new_password"))
        verify_password = Token.verify_token(token)
        if verify_password["status"]=="active":
            PasswordManager.update_password(_email, new_password)
            Token(token=token).deactivate()
            return jsonify({"message": "success"}), 200
        else:
            return jsonify({
                "detail": [
                    {
                        "loc": [
                            "token",
                            0
                        ],
                        "msg": "token is expired",
                        "type": "string"
                    }]}), 409
    except NotFound as e:
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

