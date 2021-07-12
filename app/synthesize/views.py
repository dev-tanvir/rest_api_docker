from rest_framework import viewsets, mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Tag,Chemcomp
from synthesize import serializers

class TagViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, 
                mixins.CreateModelMixin):
    """Manage Tags in the database"""
    serializer_class = serializers.TagSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    queryset = Tag.objects.all()

    def get_queryset(self):                                         # filter per user
        """Extending it show only logged user owned tags"""

        return self.queryset.filter(user=self.request.user).order_by('-name')

    def perform_create(self, serializer):
        """Create a tag"""
        serializer.save(user=self.request.user)     # This is to tag logged in user as tag user


class ChemcompViewSet(viewsets.GenericViewSet, mixins.ListModelMixin):
    """Manage Chemcomps in the database"""
    serializer_class = serializers.ChemcompSerializer
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)
    queryset = Chemcomp.objects.all()

    def get_queryset(self):                                        
        """Extending it show only logged user owned chemcomps"""

        return self.queryset.filter(user=self.request.user).order_by('-name')