import algoliasearch_django as algoliasearch
from algoliasearch_django import AlgoliaIndex
from .models import Collection, Item, Comment
from algoliasearch_django.decorators import register

@register(Item)
class ItemModel(AlgoliaIndex):
    fields = ('name', 'tag_names')
    settings = {'searchableAttributes': ['name', 'tag_names']}
    index_name = 'item_index'

algoliasearch.register(Collection)
algoliasearch.register(Comment)