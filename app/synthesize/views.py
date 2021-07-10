from rest_framework import viewsets, mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Tag
from synthesize import serializers

class TagViewSet(viewsets.GenericViewSet, mixins.ListModelMixin):
    """Manage Tags in the database"""
    serializer_class = serializers.TagSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    queryset = Tag.objects.all()

    def get_queryset(self):                                         # filter per user
        """Extending it show only logged user owned tags"""

        return self.queryset.filter(user=self.request.user).order_by('-name')
