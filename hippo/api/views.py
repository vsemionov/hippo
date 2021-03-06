from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.views.decorators.http import require_safe
from django.shortcuts import get_object_or_404
from django.http import Http404, FileResponse
from django.db.models import Q

from rest_framework import mixins, viewsets, permissions, serializers

from celery.result import AsyncResult

from .models import Job
from .serializers import JobSerializer, UserSerializer
from .permissions import JobPermissions, get_jobs_filter, get_user_jobs_filter_func
from .storage import get_content_type

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
        execute_job, link, link_error = tasks.execute_job, None, None
        if job.notify and job.owner.email:
            notify_finished, notify_failed = tasks.notify_finished, tasks.notify_failed
            link, link_error = notify_finished.si(job.owner.email, job_url), notify_failed.si(job.owner.email, job_url)
        result = execute_job.apply_async((job.id,), link=link, link_error=link_error)
        Job.objects.filter(id=job.id).update(async_id=result.id)

    def perform_destroy(self, instance):
        instance.delete()
        async_id = instance.async_id
        if async_id:
            AsyncResult(async_id).revoke()


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

@require_safe
def files(request, name):
    q = Q(input=name) | Q(output=name) | Q(results=name)
    job = get_object_or_404(Job, q)
    if not JobPermissions().has_object_permission(request, None, job):
        raise Http404()
    if job.input and job.input.name == name:
        ffile = job.input
    elif job.output and job.output.name == name:
        ffile = job.output
    elif job.results and job.results.name == name:
        ffile = job.results
    else:
        assert False
    content_type = get_content_type(ffile) or 'application/octet-stream'
    return FileResponse(ffile, content_type=content_type)
