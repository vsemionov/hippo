from django.contrib.auth.models import User
from rest_framework import serializers

from .models import Job


class JobSerializer(serializers.HyperlinkedModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')

    class Meta:
        model = Job

class UserSerializer(serializers.ModelSerializer):
    jobs = serializers.PrimaryKeyRelatedField(many=True, source='job_set', read_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'jobs')
