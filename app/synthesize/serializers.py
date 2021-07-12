from rest_framework import serializers
from core.models import Tag,Chemcomp


class TagSerializer(serializers.ModelSerializer):
    """Serializer for the tag objects"""

    class Meta:
        model = Tag
        fields = ('id', 'name')
        read_only_fields = ('id',)


class ChemcompSerializer(serializers.ModelSerializer):
    """Serializer for the chemcomp objects"""

    class Meta:
        model = Chemcomp
        fields = ('id', 'name',)
        read_only_fields = ('id',)