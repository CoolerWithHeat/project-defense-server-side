from django.db.models.signals import post_save
from django.dispatch import receiver
import algoliasearch_django as algoliasearch

from .models import Item, Collection, Comment

@receiver(post_save, sender=Item)
def update_item(sender, instance, **kwargs):
    algoliasearch.save_record(instance)

@receiver(post_save, sender=Collection)
def update_collection(sender, instance, **kwargs):
    algoliasearch.save_record(instance)

@receiver(post_save, sender=Comment)
def update_comment(sender, instance, **kwargs):
    algoliasearch.save_record(instance)