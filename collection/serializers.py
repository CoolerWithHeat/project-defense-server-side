from rest_framework import serializers
from .models import Item
from .models import Collection

class ItemSerializer(serializers.ModelSerializer):
    tags = serializers.SlugRelatedField(slug_field='name', many=True, read_only=True)
    collection = serializers.CharField(source='collection.name', read_only=True)
    class Meta:
        model = Item
        fields = ['id', 'collection', 'name', 'tags', 'additional_field_data']

class CollectionSerializer(serializers.ModelSerializer):
    author_name = serializers.SerializerMethodField()
    class Meta:
        model = Collection
        fields = ['name', 'description', 'topic', 'author', 'author_name']

    def create(self, validated_data):
        return Collection.objects.create(**validated_data)
    
    def get_author_name(self, obj):
        author = obj.author.full_name
        return author if not author == 'Not Known' else None