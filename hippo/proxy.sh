#!/bin/sh

set -e

DIR=`dirname $0`

sed -e "s/\\\$WEB_HOST/$WEB_HOST/g" -e "s/\\\$WORKER_CONNECTIONS/$WORKER_CONNECTIONS/g" $DIR/nginx.conf >/tmp/nginx.conf
ln -s /dev/null /var/log/nginx/error.log # workaround: prevent the nginx build on this image, which logs to a hard-coded location, from growing its log indefinitely
nginx -c /tmp/nginx.conf
