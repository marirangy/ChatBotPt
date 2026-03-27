#!/bin/bash

# Action server
python -m rasa_sdk --actions actions --port 5055 &

sleep 3

# Entrena y arranca
rasa train && rasa run --enable-api --cors "*" --port 10000
