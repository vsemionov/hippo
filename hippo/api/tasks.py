from functools import wraps
import socket

from django.db import OperationalError
from django.conf import settings
from django.core.mail import send_mail

from celery import shared_task

from pymongo.errors import ConnectionFailure

from .models import Job


def process_job(fn):
    @wraps(fn)
    def wrapper(job_id, job_url):
        job_filter = Job.objects.filter(id=job_id)
        job_filter.update(state=Job.STATES['started'])
        try:
            job = Job.objects.get(id=job_id)
            result = fn(job.input)
            state = Job.STATES['finished']
            return result
        except:
            state = Job.STATES['failed']
            raise
        finally:
            job_filter.update(state=state)
    return wrapper

def retry_job(fn):
    @wraps(fn)
    def wrapper(self, *args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except (socket.error, OperationalError, ConnectionFailure) as exc:
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
    pass
