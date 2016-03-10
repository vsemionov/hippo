For development environments, before deploying, run bin/mkdevenv.sh.

For production environments, before deploying, set ALLOWED_HOSTS in docker-compose.django.yml to the correct comma-separated list of values.

To deploy, install docker-engine and docker-compose, and run bin/build.sh and bin/deploy.sh.
