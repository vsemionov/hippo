Hippo
=====
A scalable distributed web application and API for asynchronous execution of [NPAmp](https://github.com/vsemionov/npamp) jobs
-----------------------------------------------------------------------------------------------------------------------------

[![Build Status](https://travis-ci.org/vsemionov/hippo.svg?branch=master)](https://travis-ci.org/vsemionov/hippo)


### Notes

This project uses *Docker* to deploy the following set of services:
* *Django*-based ReST API
* *PostgreSQL* for user and job storage
* *Celery*-based job executors
* *RabbitMQ* as a message broker
* *MongoDB* for result storage
* *Redis* for caching and session storage
* *Nginx* for proxying and serving static files (and, potentially, for load balancing)


### Installation

For development environments, before deploying, run `bin/mkdevenv.sh`.

For test environments, before deploying, run `bin/mktestenv.sh`.

For production environments, before deploying, set `ALLOWED_HOSTS` in `docker-compose.django.yml` to the correct comma-separated list of values.

To deploy, first install `docker-engine` and `docker-compose`. Optionally, to skip building and deploy from the last tested image (which, however, may be out of sync with the scripts and configuration), run `sudo docker pull vsemionov/hippo`. Finally, run `bin/deploy.sh`.


### Configuration

The configuration is contained in:
* `requirements.txt` - python dependencies and versions
* `Dockerfile` - container image build procedure
* `docker-compose.*` - service configuration and dependencies
* `hippo/hippo/settings.py` - main django-based service configuration
* `hippo/nginx.conf` - nginx configuration template
* `hippo/*.sh` - service startup scripts
* `hippo/hippo/*.conf` - additional per-service django configuration
