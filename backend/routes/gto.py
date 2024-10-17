from flask import request

from ..origin import (
    app
)
from ..settings import ServerSettings

@app.route(ServerSettings.API_PATH+'/gto/<institute_id:int>', methods=['GET'])
def get_gto(institute_name: int):
    ...