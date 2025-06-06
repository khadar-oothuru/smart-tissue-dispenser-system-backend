from django.conf import settings
from django.conf.urls.static import static

from django.contrib import admin
from django.urls import path, include, re_path
from rest_framework import permissions

from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.contrib.auth.views import LoginView

schema_view = get_schema_view(
    openapi.Info(
        title="Smart Tissue Monitoring API",
        default_version='v1',
        description="Endpoints for device management, data tracking, and alert notifications",
        contact=openapi.Contact(email="khadaroothuru@gmail.com"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('users.urls')),
    path('api/device/', include('device.urls')),
    
    path('', include('core.urls')),
    path('accounts/login/', LoginView.as_view(template_name='registration/login.html'), name='login'),

    # Swagger & Redoc Documentation
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)