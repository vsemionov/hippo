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


class ContentTypeAwareFile(File):
    def __init__(self, content_type, *args, **kwargs):
        super(ContentTypeAwareFile, self).__init__(*args, **kwargs)
        self.content_type = content_type


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
            output, results = fn(job.input, job.output, job.results)
            update.update(state=Job.STATES['finished'], output=output, results=results, error=None)
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
def execute_job(finput, foutput, fresults):
    def save_file(ffile, lfile, content_type=None):
        name = os.path.basename(lfile.name)
        with ContentTypeAwareFile(content_type, lfile) as llresults:
            ffile.save(name, llresults, save=False)
    save_output = lambda loutput, content_type: save_file(foutput, loutput, content_type)
    save_results = lambda lresults, content_type: save_file(fresults, lresults, content_type)
    try:
        execute(finput.file, save_output, save_results)
        return foutput, fresults
    except Exception as exc:
        for ffile in (foutput, fresults):
            if ffile:
                try:
                    ffile.delete(save=False)
                except Exception:
                    pass
        raise exc
