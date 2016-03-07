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


docker-compose up -d mdb

docker exec -i hippo_mdb_1 su mongodb -c bash <<EOF
set -e
echo "waiting for the database..."
until (echo > /dev/tcp/localhost/27017) &>/dev/null
do
	echo "waiting..."
	sleep 2
done
echo "try { db.createUser({'user': 'hippo', 'pwd': 'slow', 'roles': ['root']}); } catch (e) { db.auth('hippo', 'slow'); if (db.getUsers().length < 1) { db.createUser({'user': 'hippo', 'pwd': 'slow', 'roles': ['root']}); }" | mongo admin
echo
EOF
