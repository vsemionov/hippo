#!/bin/sh

docker-compose -f docker-compose.yml -f docker-compose.override.dev.yml build
