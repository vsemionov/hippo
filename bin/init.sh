#!/bin/bash

set -e

docker-compose up -d db

docker-compose run --rm web su hippo -p -c bash <<EOF
set -e
echo "waiting for the database..."
until (echo > /dev/tcp/\$DB_HOST/5432) &>/dev/null
do
	echo "waiting..."
	sleep 2
done
python manage.py migrate
echo "import os; from django.contrib.auth.models import User; User.objects.filter(is_superuser=True).count() or User.objects.create_superuser('admin', os.environ.get('ADMIN_EMAIL', 'admin@example.com'), 'admin')" | python manage.py shell
echo
EOF
