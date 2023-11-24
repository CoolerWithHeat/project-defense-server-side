from django.apps import AppConfig



class CollectionConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'collection'
    # def ready(self):
    #     from algoliasearch_django.decorators import register
    #     from .models import Item, Collection, Comment
    #     from django.db.models.signals import post_save
    #     from algoliasearch_django import AlgoliaIndex
    #     import algoliasearch_django as algoliasearch
    #     from . import signals
        
    #     @register(Item)
    #     class ItemModel(AlgoliaIndex):
    #         fields = ('name', 'tag_names')
    #         settings = {'searchableAttributes': ['name', 'tag_names']}
    #         index_name = 'item_index'
        
    #     post_save.connect(signals.update_item, sender=Item)
    #     post_save.connect(signals.update_collection, sender=Collection)
    #     post_save.connect(signals.update_comment, sender=Comment)
        
        # Register models with Algolia
        # algoliasearch.register(Item)
        # algoliasearch.register(Collection)
        # algoliasearch.registe r(Comment)