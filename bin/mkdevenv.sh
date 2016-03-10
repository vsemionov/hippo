#!/bin/sh

set -e

DIR=`dirname $0`

cd $DIR/..
cp docker-compose.override.dev.yml docker-compose.override.yml
cd hippo
openssl req -x509 -newkey rsa:2048 -nodes -keyout key.pem -out cert.pem -days 365 -subj '/CN=Hippo'
python manage.py collectstatic <<EOF
yes
EOF
