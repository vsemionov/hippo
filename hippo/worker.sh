#!/bin/sh

set -e

su -m hippo -c "celery -A hippo.celery worker --concurrency \$CONCURRENCY"
