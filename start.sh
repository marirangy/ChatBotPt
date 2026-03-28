#!/bin/bash

# Action server
python -m rasa_sdk --actions actions --port 5055 &

sleep 5

# Corre el modelo entrenado
rasa run --enable-api --cors "*" --port 10000 -i 0.0.0.0
