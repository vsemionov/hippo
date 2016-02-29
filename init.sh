#!/bin/bash

set -e

docker-compose up -d db

echo "waiting for the database..."
until docker-compose run --rm web bash -c "(echo > /dev/tcp/$DB_HOST/5432) &>/dev/null"
do
	echo "waiting..."
	sleep 2
done
docker-compose run --rm web bash -c "python manage.py migrate"
docker-compose run --rm web bash -c "echo \"from django.contrib.auth.models import User; User.objects.create_superuser('admin', 'admin@example.com', 'admin')\" | python manage.py shell"
