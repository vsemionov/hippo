from collections import OrderedDict

from django.db import models


class Job(models.Model):
    STATES = OrderedDict((
        ('pending', 'pending'),
        ('started', 'started'),
        ('finished', 'finished'),
        ('failed', 'failed'),
    ))

    state = models.CharField(choices=STATES.items(), max_length=10)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    argument = models.PositiveIntegerField()
    result = models.IntegerField(null=True)

    def save(self, *args, **kwargs):
        super(Job, self).save(*args, **kwargs)
        if self.state == self.STATES['pending']:
            import tasks
            task = tasks.power
            task.delay(job_id=self.id, n=self.argument)
