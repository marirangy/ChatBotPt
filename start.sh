#!/bin/bash

# Action server
python -m rasa_sdk --actions actions --port 5055 &

sleep 3

rasa run --enable-api --cors "*" --port ${PORT:-10000}
