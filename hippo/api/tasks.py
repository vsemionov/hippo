from functools import wraps

from celery import shared_task

from .models import Job


def update_job(fn):
    @wraps(fn)
    def wrapper(job_id, *args, **kwargs):
        job = Job.objects.get(id=job_id)
        job.state = Job.STATES['started']
        job.save()
        try:
            result = fn(*args, **kwargs)
            job.result = result
            job.state = Job.STATES['finished']
            job.save()
        except:
            job.result = None
            job.state = Job.STATES['failed']
            job.save()
    return wrapper

@shared_task
@update_job
def power(n):
    return 2 ** n
