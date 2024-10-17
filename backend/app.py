from .routes.users import *
from .routes.institutes import *

@app.route(ServerSettings.API_PATH, methods=['GET'])
def hello_world():  # put application's code here
    return "it's API"


if __name__ == '__main__':
    app.run(host=ServerSettings.HOST, port=ServerSettings.PORT, debug=True)
