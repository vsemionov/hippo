#!/bin/sh

set -e

cd hippo
su -m hippo -c "python manage.py migrate"
gunicorn -b 0.0.0.0:80 -k gevent -w 4 --max-requests 1000 -u hippo -g hippo --access-logfile - hippo.wsgi:application
