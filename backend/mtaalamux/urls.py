"""
URL configuration for mtaalamux project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path('admin/', admin.site.urls),
    # API v1
    path('api/v1/', include('core.urls')),
    # Authentication endpoints
    path('api/v1/auth/', include('core.urls_auth')),
    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Silk profiling has been disabled
# if settings.DEBUG:
#     urlpatterns += [
#         path('silk/', include('silk.urls', namespace='silk')),
#     ]
