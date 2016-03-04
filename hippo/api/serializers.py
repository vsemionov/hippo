from django.contrib.auth.models import User
from rest_framework import serializers

from .models import Job


class JobSerializer(serializers.HyperlinkedModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')

    class Meta:
        model = Job

class UserSerializer(serializers.ModelSerializer):
    # TODO: filter user jobs by matching request.user to job.owner
    jobs = serializers.HyperlinkedRelatedField(many=True, source='job_set', view_name='job-detail', read_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'jobs')
