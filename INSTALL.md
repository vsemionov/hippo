For development environments, before deploying, run bin/mkdevenv.sh.

For production environments, before deploying, set ALLOWED_HOSTS in docker-compose.django.yml to the correct comma-separated list of values (or '*').

The configuration is contained in:
* requirements.txt - python dependency versions
* Dockerfile - image build procedure
* docker-compose.* - service configuration and dependencies
* hippo/hippo/settings.py - main django-based service configuration
* hippo/nginx.conf - nginx configuration template
* hippo/*.sh - startup scripts
* hippo/hippo/*.conf - additional per-service django configuration

To deploy, install docker-engine and docker-compose and run bin/deploy.sh.
