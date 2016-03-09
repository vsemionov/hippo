import os
import socket
from functools import wraps

import django.db
from django.conf import settings
from django.core.mail import send_mail

from celery import shared_task

import pymongo.errors

from .models import Job


TRANSIENT_ERRORS = (socket.error, django.db.OperationalError, pymongo.errors.ConnectionFailure)

RESULTS_SUFFIX = "_results"


def get_results_name(input_name):
    basename = os.path.basename(input_name)
    filename, extension = os.path.splitext(basename)
    return "%s%s%s" % (filename, RESULTS_SUFFIX, extension)

def process_job(fn):
    @wraps(fn)
    def wrapper(job_id, job_url):
        job_filter = Job.objects.filter(id=job_id)
        job_filter.update(state=Job.STATES['started'])
        try:
            job = Job.objects.get(id=job_id)
            fresults = fn(job.input.file)
            results_name = get_results_name(job.input.name)
            job.results.save(results_name, fresults, save=False)
            job_filter.update(state=Job.STATES['finished'], results=job.results, error=None)
        except Exception as exc:
            job_filter.update(state=Job.STATES['failed'], error=exc)
            raise
    return wrapper

def retry_job(fn):
    @wraps(fn)
    def wrapper(self, *args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except TRANSIENT_ERRORS as exc:
            self.retry(exc=exc, countdown=30, max_retries=2**31)
    return wrapper

def notify(email, url, state):
    subject = 'Hippo job {state}'.format(state=state)
    message = 'Your Hippo job has {state}. You can view the job: {url}'.format(state=state, url=url)
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, (email,))

@shared_task(bind=True)
@retry_job
def notify_finished(email, url):
    notify(email, url, 'finished')

@shared_task(bind=True)
@retry_job
def notify_failed(email, url):
    notify(email, url, 'failed')

@shared_task(bind=True)
@retry_job
@process_job
def execute(input_file):
    return input_file
