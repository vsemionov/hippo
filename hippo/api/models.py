from collections import OrderedDict

from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError


def user_dir(instance, filename):
    return "%s/%s" % (instance.owner.username, filename)

def file_size_validator(value):
    if value.size > settings.MAX_UPLOAD_FILE_SIZE:
        raise ValidationError("Maximum file size exceeded")

class Job(models.Model):
    STATES = OrderedDict((
        ('pending', 'pending'),
        ('started', 'started'),
        ('finished', 'finished'),
        ('retrying', 'retrying'),
        ('failed', 'failed'),
    ))

    owner = models.ForeignKey('auth.User', editable=False)
    async_id = models.CharField(null=True, max_length=36, editable=False)

    public = models.BooleanField(default=False)
    notify = models.BooleanField(default=False)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    state = models.CharField(choices=STATES.items(), default=STATES['pending'], max_length=10, editable=False)

    input = models.FileField(db_index=True, upload_to=user_dir, validators=[file_size_validator])
    output = models.FileField(null=True, db_index=True, editable=False, upload_to=user_dir)
    results = models.FileField(null=True, db_index=True, editable=False, upload_to=user_dir)

    error = models.TextField(null=True, editable=False)

    def delete(self, *args, **kwargs):
        self.input.delete(save=False)
        self.results.delete(save=False)
        return super(Job, self).delete(*args, **kwargs)
