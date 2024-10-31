from audioop import cross

from ..middleware.JWT_processor import Token
from ..origin import app

from ..middleware.standard_middleware import *
from ..settings import ServerSettings


@app.route(ServerSettings.API_PATH+'/standard', methods=['GET'])
@cross_origin()
@Token.token_required
def get_standard(
        #_email
):
    res = StandardReader().get_standard
    return jsonify(res), 200


@app.route(ServerSettings.API_PATH+'/standard', methods=['POST'])
@cross_origin()
@Token.token_required
def add_standard(_email):
    try:
        name = request.json.get("name")
        res =StandardWriter(name=name).write_standard()
        return jsonify(res), 200
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
        }), 400
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


@app.route(ServerSettings.API_PATH+'/students/<int:student_id>/standards-results', methods=['GET'])
@cross_origin()
@Token.token_required
def get_standard_results(student_ud, *, _email):
    try:
        res = StandardReader(student_id=student_ud).get_res
        return jsonify(res), 200
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


@app.route(ServerSettings.API_PATH+'/students/<int:student_id>/standards', methods=['POST'])
@cross_origin()
@Token.token_required
def write_result(student_ud, *, _email):
    try:
        result = request.json.get('result')
        semester = request.json.get('semester')
        standard_id = request.json.get('standard_id')
        res = StandardWriter(
        student_id=student_ud,
        semester=semester,
        result=result,
        standard_id=standard_id
                ).write_result()
        return jsonify(res), 200
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
        }), 400
    except NoResultFound as e:
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


@app.route(ServerSettings.API_PATH+'/students/<int:student_id>/standards-results/<int:theory_result_id>',
           methods=['PATCH'])
@cross_origin()
@Token.token_required
def patch_result(student_ud, theory_result_id, *, _email):
    try:
        result = request.json.get('result')
        res = StandardWriter(
            student_id=student_ud,
            result_id=theory_result_id,
            result=result
        ).update_result()
        return jsonify(res), 200
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
        }), 400
    except NoResultFound as e:
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


@app.route(ServerSettings.API_PATH+'/students/<int:student_id>/standards-results/<int:theory_result_id>',
           methods=['DELETE'])
@cross_origin()
@Token.token_required
def delete_result(student_ud, theory_result_id, *, _email):
    try:
        res = StandardWriter(
            result_id=theory_result_id,
        ).delete_result()
        return jsonify({"message":"success"}), 200
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
        }), 400
    except NoResultFound as e:
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


