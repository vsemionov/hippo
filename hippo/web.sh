#!/bin/sh

set -e

su -m hippo -c "python manage.py migrate"
gunicorn -b 0.0.0.0:80 -k gevent -w $WORKERS --max-requests $MAX_REQUESTS -u hippo -g hippo --access-logfile - hippo.wsgi:application
