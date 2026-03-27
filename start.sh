#!/bin/bash

# Action server
python -m rasa_sdk --actions actions --port 5055 &

# Entrena en background
HOME=/tmp rasa train --out /tmp/models_new &
TRAIN_PID=$!

# Inicia Rasa sin modelo para abrir el puerto mientras entrena
rasa run --enable-api --cors "*" --port 10000 &
RASA_PID=$!

# Espera que termine el entrenamiento
wait $TRAIN_PID

# Mata el Rasa sin modelo y reinicia con el modelo entrenado
kill $RASA_PID
sleep 2
rasa run --enable-api --cors "*" --port 10000 --model /tmp/models_new
