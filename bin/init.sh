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
echo "import os; from django.contrib.auth.models import User; User.objects.filter(is_superuser=True).count() or User.objects.create_superuser(os.environ['ADMIN_USER'], os.environ['ADMIN_EMAIL'], os.environ['ADMIN_PASS'])" | python manage.py shell
echo
EOF


docker-compose up -d mdb

docker exec -i hippo_mdb_1 su mongodb -p -c bash <<EOF
set -e
echo "waiting for the database..."
until (echo > /dev/tcp/localhost/27017) &>/dev/null
do
	echo "waiting..."
	sleep 2
done
echo "try { db.createUser({'user': '\$ADMIN_USER', 'pwd': '\$ADMIN_PASS', 'roles': ['root']}); } catch (e) { db.auth('\$ADMIN_USER', '\$ADMIN_PASS'); }" | sed -e "s/\\\\\\\$ADMIN_USER/$ADMIN_USER/g" -e "s/\\\\\\\$ADMIN_PASS/$ADMIN_PASS/g" | mongo admin
EOF
