#!/bin/bash

# Limpiar caché de rasa
rm -rf .rasa/cache

# Action server
python -m rasa_sdk --actions actions --port 5055 &

sleep 3

# Entrena y arranca
rasa train --fixed-model-name modelo_nima && rasa run --enable-api --cors "*" --port 10000
