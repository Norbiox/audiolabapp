#!/bin/sh
source venv/bin/activate
while ! mysqladmin ping -h"db" -P"3306" --silent; do
    echo "Waiting for MySQL to be up..."
    sleep 1s
done
flask db upgrade
exec gunicorn -w 4 -b :5000 --access-logfile - --error-logfile - wsgi:app
