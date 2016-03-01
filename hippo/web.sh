#!/bin/sh

set -e

gunicorn -b 0.0.0.0:8000 -k gevent -w $WORKERS --max-requests $MAX_REQUESTS -u hippo -g hippo --access-logfile - hippo.wsgi:application
