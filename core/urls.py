"""
URL Configuration for core project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    # Admin
    path("admin/", admin.site.urls),
    
    # API v1
    path("api/", include("core.api_urls")),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Admin site customization
admin.site.site_header = "Manevi Rehber Admin"
admin.site.site_title = "Manevi Rehber"
admin.site.index_title = "Yönetim Paneli"
