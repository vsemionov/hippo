from collections import OrderedDict

from django.db import models


class Job(models.Model):
    STATES = OrderedDict((
        ('pending', 'pending'),
        ('started', 'started'),
        ('finished', 'finished'),
        ('failed', 'failed'),
    ))

    owner = models.ForeignKey('auth.User', editable=False)
    state = models.CharField(choices=STATES.items(), default=STATES['pending'], max_length=10, editable=False)

    public = models.BooleanField(default=False)
    notify = models.BooleanField(default=False)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    argument = models.PositiveIntegerField()
    result_id = models.CharField(null=True, max_length=36, editable=False)
