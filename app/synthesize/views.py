from rest_framework import viewsets, mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Tag, Chemcomp, Synthesize
from synthesize import serializers


class SynthesizeElementViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, 
                mixins.CreateModelMixin):
    """Manage Synthesize elements in the database"""
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):                                         # filter per user
        """Extending it show only logged user owned Synthesize elements"""
        return self.queryset.filter(user=self.request.user).order_by('-name')

    def perform_create(self, serializer):
        """Create a Synthesize elements"""
        serializer.save(user=self.request.user)     # This is to set logged in user as element user


class TagViewSet(SynthesizeElementViewSet):
    """Manage Tags in the database"""
    serializer_class = serializers.TagSerializer
    queryset = Tag.objects.all()


class ChemcompViewSet(SynthesizeElementViewSet):
    """Manage Chemcomps in the database"""
    serializer_class = serializers.ChemcompSerializer
    queryset = Chemcomp.objects.all()


class SynthesizeViewSet(SynthesizeElementViewSet):
    """Manage Synthesizes in the database"""
    serializer_class = serializers.SynthesizeSerializer
    queryset = Synthesize.objects.all()