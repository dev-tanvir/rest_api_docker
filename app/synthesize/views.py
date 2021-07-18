from rest_framework.decorators import action    #   This is to add custom action
from rest_framework.response import Response    #   This to add custom response to custom action
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
        assigned_only = bool(
            int(self.request.query_params.get('assigned_only', 0))
        )
        queryset = self.queryset

        if assigned_only:
            queryset = queryset.filter(synthesize__isnull=False)

        return queryset.filter(user=self.request.user).order_by('-name').distinct()

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
    
    def _params_to_ints(self, qs):
        """Convert a list of string IDs to list of integers"""
        return [int(str_id) for str_id in qs.split(',')]

    def get_queryset(self):                                         
        """Extending it show only logged user owned Synthesize elements"""
        tags = self.request.query_params.get('tags')
        ccs = self.request.query_params.get('chemcomps')
        queryset = self.queryset

        if tags:
            tag_ids = self._params_to_ints(tags)
            queryset = queryset.filter(tags__id__in=tag_ids)

        if ccs:
            cc_ids = self._params_to_ints(ccs)
            queryset = queryset.filter(chemcomps__id__in=cc_ids)

        return queryset.filter(user=self.request.user).order_by('-id')

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

    @action(methods=['POST'], detail=True, url_path='upload-image') # custom-url and its corresponding action
    def upload_image(self, request, pk=None):       # pk is the id of the synthesize obj. i.e. /synthesize/3/upload-image
        """Upload an image to a synthesize record"""
        synthe = self.get_object()  # using the pk, we get the object
        serializer = self.get_serializer(       # we could have set the serializer directly but get_serializer_class is recommended
            synthe,
            data=request.data,
        )

        if serializer.is_valid():
            serializer.save()       # as serializer is ModelSerializer, we can save
            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )

        return Response(
                serializer.errors,  # i.e. Upload a valid image. The file you uploaded was either not an image or a corrupted image.
                status=status.HTTP_400_BAD_REQUEST
            )