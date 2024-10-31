from datetime import datetime
import jwt

from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
import logging

import traceback

from typing import *

logging.basicConfig(filename='logging.log', level=logging.INFO)
app = Flask("health-passport", template_folder='./templates')
cors = CORS(app)
