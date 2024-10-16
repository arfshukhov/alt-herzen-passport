import json
import os

from backend.middleware.users_middleware import UserWriter, UserReader
from backend.middleware.validator import Email, Password, FullName
from origin import app

@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'

@app.route('/docs', methods=['GET'])
def get_docs():
    return json.load(open('/Users/lvv20/Documents/Pulse API.postman_collection.json'))

if __name__ == '__main__':
    print(UserReader(_id=1).get)
    app.run()
