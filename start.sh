#!/bin/bash

python init_db.py
uvicorn api.main:app --host 0.0.0.0 --port $PORT
