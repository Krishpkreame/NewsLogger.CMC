FROM python:3.11.4-slim

WORKDIR /app

COPY . /app/

RUN pip install -r requirements.txt

# Add required environment variables

ENV SELENIUM_URL 'http://127.0.0.1:4444/wd/hub'
ENV CMC_USERNAME ''
ENV CMC_PASSWORD ''
ENV MYSQL_DB1_JSON_CONN '{"host": "127.0.0.1", "user": "user", "password": "password", "database": "cmc_api"}'
ENV NTFY_URL ''

RUN chmod +x entrypoint.sh

CMD ["./entrypoint.sh"]