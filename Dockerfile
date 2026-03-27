FROM rasa/rasa:3.6.20

WORKDIR /app
COPY . /app

USER root
RUN pip install --no-cache-dir -r requirements.txt

# Eliminar el caché con permisos incorrectos y crear uno nuevo en /tmp
RUN rm -rf /app/.rasa && mkdir -p /tmp/rasa_cache && chmod 777 /tmp/rasa_cache

COPY start.sh /start.sh
RUN chmod +x /start.sh

USER 1001
ENTRYPOINT []
CMD ["/bin/bash", "/start.sh"]
