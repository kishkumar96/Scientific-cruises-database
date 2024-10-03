from django.contrib import admin
"""
URL configuration for the Pacific Cruises project.

This module defines the URL patterns for the project, including:
- Admin site routes.
- API routes from the cruises app.
- Serving media files in development.
- Serving the index.html file for all other paths (for a React app).

Routes:
- 'admin/': Admin site.
- 'api/': Includes routes from the cruises app.
- 'media/<path>': Serves media files from MEDIA_ROOT.
- '.*': Serves index.html for all other paths.

In DEBUG mode, static and media files are served from STATIC_ROOT and MEDIA_ROOT respectively.
"""
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('cruises.urls')),  # Including the API routes from cruises app
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),  # Serving media files
    # Serve index.html for all other paths (for React app)
    re_path(r'^.*$', TemplateView.as_view(template_name='index.html'), name='home'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)