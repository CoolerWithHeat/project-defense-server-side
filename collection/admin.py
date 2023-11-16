from django.contrib import admin
from .models import *

admin.site.register(User)
admin.site.register(Collection)
admin.site.register(Item)
admin.site.register(Comment)
admin.site.register(Like)
admin.site.register(Tag)
admin.site.register(CustomField)