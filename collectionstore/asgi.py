import os

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.core.asgi import get_asgi_application
from django.urls import re_path
from channels.security.websocket import AllowedHostsOriginValidator
from collection.consumers import *
from collection.full_text_search import SearchBase
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'collection.settings')

django_asgi_server = get_asgi_application()

application = ProtocolTypeRouter({
    "http": django_asgi_server,
    "https": django_asgi_server, 

    "websocket": AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter([
                # re_path("comments-flow/<int:comment_id>/", CommentsConsumer.as_asgi()),
                # re_path(r"chat/", SocketHandlers.ConsumerChatHandler.as_asgi()),
                re_path(r"comments-flow/(?P<comment_id>\w+)/", CommentsConsumer.as_asgi()),
                re_path("search/", SearchBase.as_asgi()),
                # re_path(r"ClientsMonitor/", SocketHandlers.Admin_Clients_Notification.as_asgi()),
            ])
        )
    ),

})