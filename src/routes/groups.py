import traceback
from audioop import cross

from flask import jsonify

from src.middleware.JWT_processor import Token
from src.middleware.groups_middleware import GroupsList
from src.origin import app, request, cross_origin
from src.settings import ServerSettings


@app.route(ServerSettings.API_PATH+"/groups", methods=["GET"])
@cross_origin()
@Token.token_required
def get_groups(*, _email):
    try:
        skip = int(request.args.get("skip"))
        limit = int(request.args.get("limit"))
        institute_id = int(request.args.get("institute_id"))
        course= int(request.args.get("course"))
        groups = GroupsList(
            skip=skip,
            limit=limit,
            institute_id=institute_id,
            course=course
        ).get
        return jsonify({
            "data":groups,
            "count":len(groups)
        }), 200
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
