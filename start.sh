#!/bin/bash
rasa run --enable-api --cors "*" --port 10000 -i 0.0.0.0 &
RASA_PID=$!
sleep 30
python -m rasa_sdk --actions actions --port 5055 &
wait $RASA_PID
