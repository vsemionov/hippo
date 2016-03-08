from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from rest_framework import mixins, viewsets, permissions, serializers

from celery.result import AsyncResult

from .models import Job
from .serializers import JobSerializer, UserSerializer
from .permissions import JobPermissions, get_jobs_filter, get_user_jobs_filter_func

from . import tasks


class JobViewSet(mixins.CreateModelMixin,
                 mixins.ListModelMixin,
                 mixins.RetrieveModelMixin,
                 mixins.DestroyModelMixin,
                 viewsets.GenericViewSet):
    queryset = Job.objects.all()
    serializer_class = JobSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, JobPermissions)

    def get_queryset(self):
        return get_jobs_filter(self.request)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
        job = serializer.instance
        job_url = self.request.build_absolute_uri(reverse('job-detail', args=[job.id]))
        execute, link, link_error = tasks.execute, None, None
        if job.notify and job.owner.email:
            notify_finished, notify_failed = tasks.notify_finished, tasks.notify_failed
            link, link_error = notify_finished.si(job.owner.email, job_url), notify_failed.si(job.owner.email, job_url)
        result = execute.apply_async((job.id, job_url), link=link, link_error=link_error)
        Job.objects.filter(id=job.id).update(result_id=result.id)

    def perform_destroy(self, instance):
        instance.delete()
        result_id = instance.result_id
        if result_id:
            AsyncResult(result_id).revoke()


class UserViewSet(mixins.ListModelMixin,
                  mixins.RetrieveModelMixin,
                  viewsets.GenericViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAuthenticated,)

    # ugly hack to filter jobs related to users
    # failed: https://github.com/tomchristie/django-rest-framework/issues/1985
    # failed: https://github.com/tomchristie/django-rest-framework/issues/1935
    def get_serializer(self, *args, **kwargs):
        serializer = super(UserViewSet, self).get_serializer(*args, **kwargs)
        userser = serializer if not isinstance(serializer, serializers.ListSerializer) else serializer.child
        userser.fields['jobs'].get_attribute = get_user_jobs_filter_func(self.request)
        return serializer
