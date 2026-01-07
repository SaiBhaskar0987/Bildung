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

# Import the FastAPI app module and get the app instance
from aiassist import app as fastapi_module

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

# Custom ASGI router to split traffic
class PathRouter:
    def __init__(self, fastapi_app, django_app):
        self.fastapi_app = fastapi_app
        self.django_app = django_app

    async def __call__(self, scope, receive, send):
        path = scope.get("path", "")
        if scope["type"] == "http" and (path.startswith("/api/ai") or path in ["/docs", "/openapi.json"]):
            # Adjust path for FastAPI (strip /api/ai prefix if present)
            if path.startswith("/api/ai"):
                scope["path"] = path[7:]  # Remove "/api/ai" prefix
            await self.fastapi_app(scope, receive, send)
        else:
            await self.django_app(scope, receive, send)

# Django's ASGI app
django_asgi_app = get_asgi_application()

# Combined HTTP app
http_app = PathRouter(fastapi_module.app, django_asgi_app)

application = ProtocolTypeRouter({
    "http": http_app,
    "websocket": AuthMiddlewareStack(
        URLRouter(chat.routing.websocket_urlpatterns)
    ),
})