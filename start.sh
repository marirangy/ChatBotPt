#!/bin/bash

# Action server
python -m rasa_sdk --actions actions --port 5055 &

sleep 3

# Entrena usando /tmp para el caché (tiene permisos de escritura)
RASA_HOME=/tmp rasa train --out /tmp/models_new && rasa run --enable-api --cors "*" --port 10000 --model /tmp/models_new
