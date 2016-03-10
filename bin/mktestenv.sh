#!/bin/sh

set -e

DIR=`dirname $0`

cd $DIR/..
cp docker-compose.test.yml docker-compose.override.yml
