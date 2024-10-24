from werkzeug.routing import ValidationError

from src.settings import ServerSettings
from ..middleware.JWT_processor import Token
from ..middleware.students_middleware import StudentsReader, StudentWriter
from ..origin import *


@app.route(ServerSettings.API_PATH+"/students/<int:student_id>", methods=["GET"])
@Token.token_required
def get_student(student_id: int, *, _email):
    try:
        student_id = int(student_id)
        student = StudentsReader(_id=student_id).get
        return jsonify(student), 200
    except Exception as e:
        logging.error(e)
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


@app.route(ServerSettings.API_PATH+"/students/", methods=["POST"])
def write_student():
    try:
        jsn = dict(request.json)
        query = StudentWriter(data=jsn).write()
        return jsonify(query), 200
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
        }), 403
    except ValueError as e:
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
        logging.error(e)
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






@app.route(ServerSettings.API_PATH+"/students/<int:student_id>", methods=["PATCH"])
@Token.token_required
def update_student(student_id: int, *, _email):
    try:
        jsn = dict(request.json)
        query = StudentWriter(_id=student_id, data=jsn).update()
        return jsonify(query), 200
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
        }), 403
    except ValueError as e:
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


@app.route(ServerSettings.API_PATH+"/students/<int:student_id>", methods=["DELETE"])
@Token.token_required
def delete_student(student_id: int, *, _email):
    try:
        StudentWriter(_id=student_id).delete()
        return jsonify({"message": "success"}), 200
    except KeyError as e:
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
