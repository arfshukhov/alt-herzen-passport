import json
import os

from backend.middleware.users_middleware import UserWriter, UserReader
from backend.middleware.validator import Email, Password, FullName
from backend.settings import ServerSettings
from origin import app
from routes.users import *

@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'


if __name__ == '__main__':
    app.run(host='0.0.0.0'+ServerSettings.API_TAIL)
