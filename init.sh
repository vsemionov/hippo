#!/bin/bash

set -e

docker-compose up -d db

echo "waiting for database"
until docker-compose run --rm web bash -c "cd hippo && python manage.py migrate 2>/dev/null"
do
	sleep 1
done
