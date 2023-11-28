import os
import django.conf

from channels.routing import ProtocolTypeRouter, URLRouter
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'collectionstore.settings')
import django
django.setup()
from channels.auth import AuthMiddlewareStack
from django.core.asgi import get_asgi_application
from django.urls import re_path
from channels.security.websocket import AllowedHostsOriginValidator
from collection.consumers import *
from collection.tagAuto_complete import TagRecommendation


django_asgi_server = get_asgi_application()

application = ProtocolTypeRouter({
    "http": django_asgi_server,

    "websocket": AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter([
                re_path(r"comments-flow/(?P<item_id>\w+)/", CommentsConsumer.as_asgi()),
                re_path("search/", TagRecommendation.as_asgi()),
            ])
        )
    ),

})