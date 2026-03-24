FROM rasa/rasa:3.6.20

WORKDIR /app

COPY . /app

USER root

RUN pip install --no-cache-dir -r requirements.txt

USER 1001

CMD ["run", "--enable-api", "--cors", "*", "--port", "10000"]
