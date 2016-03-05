from functools import wraps

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
            job.refresh_from_db()
            job.result = result
            job.state = Job.STATES['finished']
        except:
            job.refresh_from_db()
            job.result = None
            job.state = Job.STATES['failed']
        finally:
            job.save()
            if job.notify and job.owner.email:
                notify.delay(job.owner.email, job_url)
    return wrapper

@shared_task
def notify(owner_email, job_url):
    subject = 'Hippo job completed'
    message = 'Your Hippo job has been completed. You can view the results here: {url}'.format(url=job_url)
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, (owner_email,))

@shared_task
@process_job
def power(n):
    return 2 ** n
