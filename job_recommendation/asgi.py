import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.urls import path
from jobs.consumers import JobConsumer

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'job_recommendation.settings')

# The ASGI application
application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter([
            path("ws/jobs/", JobConsumer.as_asgi()),
        ])
    ),
})
