from flask import Flask, request
from flask_cors import CORS

app = Flask("health-passport")
CORS(app)