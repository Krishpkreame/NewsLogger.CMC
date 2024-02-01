FROM python:3.11.4-slim

WORKDIR /app

COPY . /app/

RUN pip install -r requirements.txt

# Add required environment variables

# ENV SELENIUM_URL 
# ENV CMC_USERNAME 
# ENV CMC_PASSWORD 
# ENV MYSQL_DB1_JSON_CONN 
# ENV NTFY_URL 

RUN chmod +x entrypoint.sh

CMD ["./entrypoint.sh"]