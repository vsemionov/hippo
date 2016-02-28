#!/bin/sh

set -e

su -m hippo -c "celery worker -A hippo.celery"
