from .routes.users import *

@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'


if __name__ == '__main__':
    app.run(host=ServerSettings.HOST, port=ServerSettings.PORT, debug=True)
