from datetime import datetime

from flask import Flask, request, jsonify
from flask_cors import CORS
import logging

logging.basicConfig(filename='logging.log', level=logging.INFO)

app = Flask("health-passport")
CORS(app)