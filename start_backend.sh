#!/bin/bash

export HOST=127.0.0.1
export PORT=8888

pip install -r src/requirements.txt

gunicorn --bind=$HOST:$PORT "src.app:app"