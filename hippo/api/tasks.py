import os
import socket
from functools import wraps

import django.db
from django.conf import settings
from django.utils.timezone import now
from django.core.mail import send_mail
from django.core.files.base import File

from celery import shared_task

import pymongo.errors

from .models import Job
from .execution import execute


TRANSIENT_ERRORS = (socket.error, django.db.OperationalError, pymongo.errors.ConnectionFailure)


def retry_job(fn):
    @wraps(fn)
    def wrapper(self, *args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except TRANSIENT_ERRORS as exc:
            self.retry(exc=exc, countdown=30, max_retries=2**31)
    return wrapper

def process_job(fn):
    @wraps(fn)
    def wrapper(job_id):
        job_filter = Job.objects.filter(id=job_id)
        job_filter.update(updated=now(), state=Job.STATES['started'])
        update = {}
        try:
            job = Job.objects.get(id=job_id)
            results = fn(job.input, job.results)
            update.update(state=Job.STATES['finished'], results=results, error=None)
        except TRANSIENT_ERRORS as exc:
            update.update(state=Job.STATES['retrying'], error=exc)
            raise
        except Exception as exc:
            update.update(state=Job.STATES['failed'], error=exc)
            raise
        finally:
            if update:
                try:
                    job_filter.update(updated=now(), **update)
                except Exception:
                    pass
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
def execute_job(finput, fresults):
    def save_results(lresults):
        name = os.path.basename(lresults.name)
        with File(lresults) as llresults:
            fresults.save(name, llresults, save=False)
    execute(finput.file, save_results)
    return fresults
