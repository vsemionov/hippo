from django.contrib.auth.models import User
from rest_framework import mixins, viewsets, permissions, serializers

from .models import Job
from .serializers import JobSerializer, UserSerializer
from .permissions import JobPermissions, get_jobs_filter, get_user_jobs_filter_func


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


# ugly hack to filter jobs related to users
# failed: https://github.com/tomchristie/django-rest-framework/issues/1985
# failed: https://github.com/tomchristie/django-rest-framework/issues/1935
class SecuredFieldMixin(object):
    def get_serializer(self, *args, **kwargs):
        serializer = super(SecuredFieldMixin, self).get_serializer(*args, **kwargs)
        userser = serializer if not isinstance(serializer, serializers.ListSerializer) else serializer.child
        userser.fields['jobs'].get_attribute = get_user_jobs_filter_func(self.request)
        return serializer

class UserViewSet(SecuredFieldMixin, mixins.ListModelMixin,
                  mixins.RetrieveModelMixin,
                  viewsets.GenericViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAuthenticated,)
