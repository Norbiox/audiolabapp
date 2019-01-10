FROM python:3.6-alpine

RUN adduser -D labapp

WORKDIR /home/labapp

RUN apk add python-dev python3-dev 
RUN apk add --no-cache mariadb-connector-c-dev ;\
    apk add --no-cache --virtual .build-deps \
        build-base \
        mariadb-dev ;\
    pip install mysqlclient;\
    apk del .build-deps
RUN apk add --no-cache mysql-client

COPY requirements.txt requirements.txt
RUN python -m venv venv
RUN venv/bin/pip install -r requirements.txt
RUN venv/bin/pip install gunicorn

COPY app app
COPY migrations migrations
COPY boot.sh wsgi.py ./
RUN chmod +x boot.sh

ENV FLASK_APP=wsgi:app

RUN chown -R labapp:labapp ./
USER labapp

EXPOSE 80
ENTRYPOINT ["./boot.sh"]
