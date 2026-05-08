"""
URL Configuration for core project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse


def health_check(request):
    """Health check endpoint"""
    from django.db import connection
    
    try:
        connection.ensure_connection()
        db_status = "connected"
    except Exception:
        db_status = "disconnected"
    
    return JsonResponse({
        "status": "healthy" if db_status == "connected" else "unhealthy",
        "database": db_status,
        "timestamp": str(timezone.now()),
    })


urlpatterns = [
    # Admin
    path("admin/", admin.site.urls),
    
    # Health check
    path("health/", health_check, name="health-check"),
    
    # API v1
    path("api/", include("core.urls")),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Admin site customization
admin.site.site_header = "Manevi Rehber Admin"
admin.site.site_title = "Manevi Rehber"
admin.site.index_title = "Yönetim Paneli"
