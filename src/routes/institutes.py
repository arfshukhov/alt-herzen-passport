from audioop import cross



from ..middleware.institute_middleware import InstitutesList
from ..origin import (
    app, request, jsonify, traceback, cross_origin
)
from ..settings import ServerSettings


@app.route(ServerSettings.API_PATH+'/institutes', methods=['GET'])
@cross_origin
def get_institutes():
    try:
        skip = int(request.json.get("skip"))
        limit = int(request.json.get("limit"))
        institutes = InstitutesList(skip=skip, limit=limit).get
        res = {
            "data": list(institutes),
            "count": len(institutes)
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