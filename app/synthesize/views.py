from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets, mixins, status
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


class SynthesizeViewSet(viewsets.ModelViewSet):
    """Manage Synthesizes in the database"""
    serializer_class = serializers.SynthesizeSerializer
    queryset = Synthesize.objects.all()
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    
    def get_queryset(self):                                         
        """Extending it show only logged user owned Synthesize elements"""
        return self.queryset.filter(user=self.request.user).order_by('-id')

    def get_serializer_class(self):
        """Return the appropriate serializer class"""
        # print(self.action)
        if self.action == 'retrieve':
            return serializers.SynthesizeDetailSerializer

        elif self.action == 'upload_image':
            return serializers.SynthesizeImageUploadSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        """Create a Synthesize elements"""
        serializer.save(user=self.request.user)

    @action(methods=['POST'], detail=True, url_path='upload-image')
    def upload_image(self, request, pk=None):
        """Upload an image to a synthesize record"""
        synthe = self.get_object()
        serializer = self.get_serializer(
            synthe,
            data=request.data,
        )

        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )

        return Response(
                serializer.data,
                status=status.HTTP_400_BAD_REQUEST
            )