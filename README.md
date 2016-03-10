Hippo
=====
A scalable distributed web application and API for asynchronous execution of NPAmp jobs
---------------------------------------------------------------------------------------

[![Build Status](https://travis-ci.org/vsemionov/hippo.svg?branch=master)](https://travis-ci.org/vsemionov/hippo)


### Installation

For development environments, before deploying, run `bin/mkdevenv.sh`.

For test environments, before deploying, run `bin/mktestenv.sh`.

For production environments, before deploying, set `ALLOWED_HOSTS` in `docker-compose.django.yml` to the correct comma-separated list of values.

To deploy, first install `docker-engine` and `docker-compose`. Optionally, to skip building and deploy from the last tested image (which, however, may be out of sync with the scripts and configuration), run `sudo docker pull vsemionov/hippo:tested`. Finally, run `bin/deploy.sh`.


### Configuration

The configuration is contained in:
* requirements.txt - python dependency versions
* Dockerfile - image build procedure
* docker-compose.\* - service configuration and dependencies
* hippo/hippo/settings.py - main django-based service configuration
* hippo/nginx.conf - nginx configuration template
* hippo/\*.sh - startup scripts
* hippo/hippo/\*.conf - additional per-service django configuration
