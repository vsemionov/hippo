#!/bin/sh

set -e

DIR=`dirname $0`

sed -e "s/\\\$WEB_HOST/$WEB_HOST/g" -e "s/\\\$WORKER_CONNECTIONS/$WORKER_CONNECTIONS/g" $DIR/nginx.conf >/tmp/nginx.conf
nginx -c /tmp/nginx.conf
