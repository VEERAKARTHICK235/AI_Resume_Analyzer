from django.contrib import admin
from django.urls import path
from analyzer import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.upload_resume, name='upload_resume'),
    path('result/', views.result, name='result'),
    path('download-pdf/', views.download_pdf, name='download_pdf'),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    # Optional: serve static files (e.g., favicon) if not using collectstatic
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
