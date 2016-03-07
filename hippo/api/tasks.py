from functools import wraps
import socket

from django.db import OperationalError
from django.conf import settings
from django.core.mail import send_mail

from celery import shared_task

from .models import Job


def process_job(fn):
    @wraps(fn)
    def wrapper(job_id, job_url):
        job = Job.objects.get(id=job_id)
        job.state = Job.STATES['started']
        job.save()
        try:
            result = fn(job.argument)
            job.result = result
            job.state = Job.STATES['finished']
        except:
            job.result = None
            job.state = Job.STATES['failed']
        finally:
            job.save()
            if job.notify and job.owner.email:
                notify.delay(job.owner.email, job_url)
    return wrapper

def retry_job(fn):
    @wraps(fn)
    def wrapper(self, *args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except (socket.error, OperationalError) as exc:
            self.retry(exc=exc, countdown=30, max_retries=2**31)
    return wrapper

@shared_task(bind=True)
@retry_job
def notify(owner_email, job_url):
    subject = 'Hippo job completed'
    message = 'Your Hippo job has been completed. You can view the results here: {url}'.format(url=job_url)
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, (owner_email,))

@shared_task(bind=True)
@retry_job
@process_job
def power(n):
    return 2 ** n
