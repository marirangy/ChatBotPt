#!/bin/bash

# 1) Action server (equivale a "rasa run actions")
python -m rasa_sdk --actions actions --port 5055 &

# Espera a que levante
sleep 3

# 2) Rasa principal (equivale a "rasa run")
rasa run --enable-api --cors "*" --port 10000
