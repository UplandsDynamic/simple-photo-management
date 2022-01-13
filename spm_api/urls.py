from django.contrib import admin
from django.urls import path, re_path
from django.conf.urls import include
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
                  path('admin/', admin.site.urls),
                  re_path(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
                  re_path(r'^api/', include('spm_app.urls', namespace='spm_api')),
              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
