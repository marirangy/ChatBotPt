#!/bin/bash

# Action server
python -m rasa_sdk --actions actions --port 5055 &

sleep 3

# Entrena en Render y arranca
rasa train --out models_new && rasa run --enable-api --cors "*" --port 10000 --model models_new
