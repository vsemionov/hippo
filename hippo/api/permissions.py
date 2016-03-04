from django.db.models import Q
from rest_framework import permissions

from .models import Job


class JobPermissions(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user.is_superuser or request.user == obj.owner or request.method in permissions.SAFE_METHODS and obj.public

def get_jobs_filter_arg(request):
    q = Q(public=True)
    if request.user.is_authenticated():
        q |= Q(owner=request.user)
    return q

def get_jobs_filter(request):
    if request.user.is_superuser:
        return Job.objects.all()
    q = get_jobs_filter_arg(request)
    return Job.objects.filter(q)

def get_user_jobs_filter_func(request):
    def user_jobs_filter_func(instance):
        job_set = instance.job_set
        if request.user.is_superuser:
            return job_set.all()
        q = get_jobs_filter_arg(request)
        return instance.job_set.filter(q)
    return user_jobs_filter_func
