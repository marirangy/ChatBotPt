#!/bin/bash

python -m rasa_sdk --actions actions --port 5055 &

sleep 3

HOME=/tmp rasa train --out /tmp/models_new && rasa run --enable-api --cors "*" --port 10000 --model /tmp/models_new
