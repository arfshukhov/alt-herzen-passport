from audioop import cross

from flask import request, jsonify
from flask_cors import cross_origin
from sqlalchemy.exc import NoResultFound
from werkzeug.routing import ValidationError

from ..middleware.JWT_processor import Token
from ..middleware.gto_middleware import AssemblerGTO, GTOWriter
from ..origin import (
    app, traceback
)
from ..settings import ServerSettings

@app.route(ServerSettings.API_PATH+'/gto', methods=['GET'])
@cross_origin()
@Token.token_required
def get_gto(*, _email):
    try:
        institute_id = int(request.args.get('institute_id'))
        gto_table = AssemblerGTO(institute_id=institute_id).get
        return jsonify(gto_table), 200
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


@app.route(ServerSettings.API_PATH+'/gto', methods=['POST'])
@cross_origin()
@Token.token_required
def post_gto(*, _email):
    try:
        level = request.json.get('level')
        student_id = request.json.get('student_id')
        gto = GTOWriter(
            student_id=student_id,
            level=level,
        ).write()
        return jsonify({gto}), 200
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


@app.route(ServerSettings.API_PATH+'/gto_update', methods=['UPDATE'])
@cross_origin()
@Token.token_required
def update_gto(*, _email):
    try:
        level = request.json.get('level')
        student_id = request.json.get('student_id')
        gto = GTOWriter(
            student_id=student_id,
            level=level,
        ).update()
        return jsonify({gto}), 200
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
        }), 406
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