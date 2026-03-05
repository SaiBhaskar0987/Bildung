"""
ASGI config for core project.

It exposes the ASGI callable as a module-level variable named ``application``.

https://docs.djangoproject.com/en/5.0/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

from starlette.applications import Starlette
from starlette.routing import Mount

import chat.routing

from fastapi_app.main_app import app as fastapi_app


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

django_asgi_app = get_asgi_application()


http_app = Starlette(
    routes=[
        Mount("/api", app=fastapi_app),    
        Mount("/", app=django_asgi_app),    
    ]
)


application = ProtocolTypeRouter({
    "http": http_app,
    "websocket": AuthMiddlewareStack(
        URLRouter(chat.routing.websocket_urlpatterns)
    ),
})
