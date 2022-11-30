"""
ASGI config for teleasistencia project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/asgi/
"""

import os
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from alarmasApp import routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'teleasistencia.settings')

application = ProtocolTypeRouter({
    'websocket':AuthMiddlewareStack(
        URLRouter(
            routing.websocket_urlpatterns
        )
    )
})
