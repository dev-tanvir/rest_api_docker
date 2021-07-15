from rest_framework import serializers
from core.models import Tag, Chemcomp, Synthesize


class TagSerializer(serializers.ModelSerializer):
    """Serializer for the tag objects"""

    class Meta:
        model = Tag
        fields = ('id', 'name',)
        read_only_fields = ('id',)


class ChemcompSerializer(serializers.ModelSerializer):
    """Serializer for the chemcomp objects"""

    class Meta:
        model = Chemcomp
        fields = ('id', 'name',)
        read_only_fields = ('id',)


class SynthesizeSerializer(serializers.ModelSerializer):
    """Serializer for the Synthesize objects"""
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset = Tag.objects.all()
    )

    chemcomps = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset = Chemcomp.objects.all()
    )

    class Meta:
        model = Synthesize
        fields = ('id','title','time_years','chance','link','tags','chemcomps',)
        read_only_fields = ('id',)