"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path
from rest_framework.renderers import JSONOpenAPIRenderer
from rest_framework.schemas import get_schema_view

schema_view = get_schema_view(
    title='Dating Backend API',
    description='OpenAPI schema for the Dating Backend REST API.',
    version='1.0.0',
    public=True,
    renderer_classes=[JSONOpenAPIRenderer],
)

urlpatterns = [
    path('api/schema/', schema_view, name='openapi-schema'),
    path('dashboard/', include('dashboard.urls')),
    path('api/auth/', include('accounts.urls')),
    path('api/profiles/', include('profiles.urls')),
    path('api/matches/', include('dating.urls')),
    path('api/chats/', include('chat.urls')),
    path('api/notifications/', include('notifications.urls')),
    path('api/reports/', include('reports.urls')),
    path('api/subscriptions/', include('subscriptions.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
