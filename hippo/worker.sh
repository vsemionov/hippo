#!/bin/sh

set -e

export LOCAL_SETTINGS_FILE=/hippo/hippo/hippo/worker.conf
su -m hippo -c "celery -A hippo.celery worker --concurrency \$CONCURRENCY --maxtasksperchild \$MAX_TASKS_PER_CHILD --loglevel INFO"
