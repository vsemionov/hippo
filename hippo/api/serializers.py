from django.contrib.auth.models import User
from rest_framework import serializers

from .models import Job


class JobSerializer(serializers.HyperlinkedModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')

    class Meta:
        model = Job
        exclude = ('async_id',)

class UserSerializer(serializers.ModelSerializer):
    jobs = serializers.HyperlinkedRelatedField(many=True, source='job_set', view_name='job-detail', read_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'jobs')
