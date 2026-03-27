#!/bin/bash

# Action server
python -m rasa_sdk --actions actions --port 5055 &

sleep 3

# Rasa con el modelo específico
rasa run --enable-api --cors "*" --port 10000 --model models/20260323-165757-coincident-world.tar.gz
