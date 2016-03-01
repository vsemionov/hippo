#!/bin/sh

set -e

supervisord -c conf/supervisord.conf
