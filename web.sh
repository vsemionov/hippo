#!/bin/sh

set -e

cd hippo
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
