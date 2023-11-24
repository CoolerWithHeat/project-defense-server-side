from rest_framework import serializers
from .models import Item, Collection
from django.contrib.auth import get_user_model

User = get_user_model()

class ItemSerializer(serializers.ModelSerializer):
    tags = serializers.SlugRelatedField(slug_field='name', many=True, read_only=True)
    collection = serializers.CharField(source='collection.name', read_only=True)
    class Meta:
        model = Item
        fields = ['id', 'collection', 'name', 'tags', 'additional_field_data']

class CollectionSerializer(serializers.ModelSerializer):
    author_name = serializers.SerializerMethodField()
    image = serializers.FileField(required=False)
    description = serializers.CharField(required=False)
    class Meta:
        model = Collection
        fields = ['id', 'name', 'description', 'topic', 'author', 'author_name', 'image']

    def create(self, validated_data):
        return Collection.objects.create(**validated_data)
    
    def get_author_name(self, obj):
        author = obj.author.full_name
        return author if not author == 'Not Known' else None

class UserSerializer(serializers.ModelSerializer):
    blocked = serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = ['id', 'blocked', 'full_name', 'admin']
    
    def get_blocked(self, obj):
        return 'NO' if obj.is_active else 'YES'