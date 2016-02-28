#!/bin/sh

set -e

cd hippo
su -m hippo -c "celery worker -A hippo.celery"
