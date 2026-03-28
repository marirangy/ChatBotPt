#!/bin/bash
rasa run --enable-api --cors "*" --port ${PORT:-5005} -i 0.0.0.0 --endpoints endpoints.render.yml
