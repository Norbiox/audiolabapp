#!/bin/sh
source venv/bin/activate
flask db upgrade
exec gunicorn -w 4 -b :5000 --access-logfile - --error-logfile - wsgi:app
