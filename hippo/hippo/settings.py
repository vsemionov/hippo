"""
Django settings for hippo project.

Generated by 'django-admin startproject' using Django 1.9.2.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.9/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.9/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '5jd5p#^0a_v1!(9_)q#$pzr(84#ls)b%fc!db-#7gc@y83ax9f'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = [host.strip() for host in os.environ.get('ALLOWED_HOSTS', '*').split(',')]


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'api',
]

MIDDLEWARE_CLASSES = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'hippo.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'hippo.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.9/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'NAME': os.environ.get('DB_DB', 'postgres'),
        'USER': os.environ.get('DB_USER', 'postgres'),
        'PASSWORD': os.environ.get('DB_PASS', ''),
        'CONN_MAX_AGE': 1800,
    }
}


# Password validation
# https://docs.djangoproject.com/en/1.9/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/1.9/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')


# Cache

CACHES = {
    'default': {
        'BACKEND': 'redis_cache.RedisCache',
        'LOCATION': '{host}:6379'.format(host=os.environ.get('RDB_HOST', 'localhost')),
        'OPTIONS': {
            'DB': int(os.environ.get('RDB_CACHE_DB', '0')),
            'PASSWORD': os.environ.get('RDB_PASS', ''),
            'SOCKET_TIMEOUT': 5,
            'SOCKET_CONNECT_TIMEOUT': 5,
            'CONNECTION_POOL_CLASS': 'redis.BlockingConnectionPool',
            'CONNECTION_POOL_CLASS_KWARGS': {
                'max_connections': 50,
                'timeout': 20,
            },
        },
    },
}

SESSION_ENGINE = 'django.contrib.sessions.backends.cache'


# Celery

BROKER_URL = os.environ.get('BROKER_URL', '')
if not BROKER_URL:
    BROKER_URL = 'amqp://{user}:{password}@{host}/{vhost}/'.format(
        user=os.environ.get('MQ_USER', 'guest'),
        password=os.environ.get('MQ_PASS', 'guest'),
        host=os.environ.get('MQ_HOST', 'localhost'),
        vhost=os.environ.get('MQ_VHOST', '')
    )

BROKER_HEARTBEAT = 60

BROKER_POOL_LIMIT = 10

CELERY_ACKS_LATE = True

CELERY_IGNORE_RESULT = False
CELERY_TASK_RESULT_EXPIRES = 24*60*60
CELERY_MAX_CACHED_RESULTS = 5000

CELERY_RESULT_BACKEND = 'redis://:%s@%s/%s' % (os.environ.get('RDB_PASS', ''), os.environ.get('RDB_HOST', 'localhost'), os.environ.get('RDB_TASK_DB', '1'))
CELERY_REDIS_MAX_CONNECTIONS = 100

# Don't use pickle as serializer, json is much safer
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_ACCEPT_CONTENT = ['json']

CELERYD_PREFETCH_MULTIPLIER = 1

CELERYD_HIJACK_ROOT_LOGGER = False


# REST framework

REST_FRAMEWORK = {
    'PAGE_SIZE': 10,
}


# Email

SERVER_EMAIL = os.environ.get('ADMIN_EMAIL', 'admin@example.com')
DEFAULT_FROM_EMAIL = SERVER_EMAIL

EMAIL_HOST_USER = os.environ.get('EMAIL_USER', 'admin')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_PASS', '')

EMAIL_HOST = os.environ.get('EMAIL_HOST', 'localhost')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', '25'))
EMAIL_USE_TLS = bool(os.environ.get('EMAIL_USE_TLS', '0'))

ADMINS = (
    (os.environ.get('ADMIN_NAME', 'Hippo Admin'), SERVER_EMAIL),
)

MANAGERS = (
    (os.environ.get('ADMIN_NAME', 'Hippo Admin'), SERVER_EMAIL),
)


# Local settings

LOCAL_SETTINGS_FILE = os.environ.get('LOCAL_SETTINGS_FILE')
if LOCAL_SETTINGS_FILE:
    exec open(LOCAL_SETTINGS_FILE) in globals()
