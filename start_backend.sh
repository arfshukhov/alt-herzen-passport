#!/bin/bash

export HOST=127.0.0.1
export PORT=8888

pip install -r requirements.txt


gunicorn --bind=$HOST:$PORT "backend.app:app"