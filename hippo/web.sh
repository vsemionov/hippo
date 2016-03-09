#!/bin/sh

set -e

gunicorn -b 0.0.0.0:8000 -u hippo -g hippo -k gevent -w $WORKERS --worker-connections $WORKER_CONNECTIONS --max-requests $MAX_REQUESTS --access-logfile - $ARGS hippo.wsgi:application
