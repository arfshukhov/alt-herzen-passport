from datetime import datetime
import jwt
from flask import Flask, request, jsonify
from flask_cors import CORS
import logging

import traceback

from typing import *

logging.basicConfig(filename='logging.log', level=logging.INFO)
app = Flask("health-passport")
CORS(app)