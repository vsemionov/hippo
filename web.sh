#!/bin/sh

set -e

cd hippo
python manage.py migrate
gunicorn -b 0.0.0.0:8000 -k gevent -w 4 --max-requests 1000 --access-logfile - hippo.wsgi:application
