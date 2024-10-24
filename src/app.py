from os import rename

from flask import render_template

from .routes.users import *
from .routes.institutes import *
from .routes.groups import *
from .routes.gto import *
from .routes.students import *
from .routes.login import *

@app.route(ServerSettings.API_PATH+"/docs", methods=['GET'])
def hello_world():  # put application's code here
    return render_template("swaggerui.html")


if __name__ == '__main__':
    app.run(host=ServerSettings.HOST, port=ServerSettings.PORT, debug=True)
