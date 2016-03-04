from django.contrib.auth.models import User
from django.db.models import Q
from rest_framework import mixins, viewsets, permissions

from .models import Job
from .serializers import JobSerializer, UserSerializer
from .permissions import JobPermissions


class JobViewSet(mixins.CreateModelMixin,
                 mixins.ListModelMixin,
                 mixins.RetrieveModelMixin,
                 mixins.DestroyModelMixin,
                 viewsets.GenericViewSet):
    queryset = Job.objects.all()
    serializer_class = JobSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, JobPermissions)

    def get_queryset(self):
        q = Q(public=True)
        if self.request.user.is_authenticated():
            q |= Q(owner=self.request.user)
        return Job.objects.filter(q)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

class UserViewSet(mixins.ListModelMixin,
                 mixins.RetrieveModelMixin,
                 viewsets.GenericViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
