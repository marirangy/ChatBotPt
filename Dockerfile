FROM rasa/rasa:3.6.20

WORKDIR /app
COPY . /app

USER root
RUN pip install --no-cache-dir -r requirements.txt
COPY start.sh /start.sh
RUN chmod +x /start.sh

USER 1001
ENTRYPOINT []
CMD ["/bin/bash", "/start.sh"]
