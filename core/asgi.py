"""
ASGI config for core project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/asgi/
"""

#import os

#from django.core.asgi import get_asgi_application

#os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

#application = get_asgi_application()

# core/asgi.py
# core/asgi.py
import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import chat.routing
from starlette.applications import Starlette
from starlette.routing import Mount
# Import the FastAPI app module and get the app instance
from aiassist.app import app as fastapi_module


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

django_asgi_app = get_asgi_application()

starlette_app = Starlette(routes=[
    Mount("/api/ai", app=fastapi_module),
    Mount("/", app=django_asgi_app),
])

application = ProtocolTypeRouter({
    "http": starlette_app,
    "websocket": AuthMiddlewareStack(
        URLRouter(chat.routing.websocket_urlpatterns)
    ),
})