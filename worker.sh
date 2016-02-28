#!/bin/sh

set -e

cd hippo
celery worker -A hippo.celery
