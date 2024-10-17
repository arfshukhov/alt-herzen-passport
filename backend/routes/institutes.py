from ..middleware.institute_middleware import InstitutesList
from ..origin import (
    app, request, jsonify
)
from ..settings import ServerSettings


@app.route(ServerSettings.API_PATH+'/institutes', methods=['GET'])
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