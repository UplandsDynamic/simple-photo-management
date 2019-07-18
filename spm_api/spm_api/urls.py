from django.contrib import admin
from django.urls import path
from django.conf.urls import url, include
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
                  path('admin/', admin.site.urls),
                  url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
                  url(r'^api/', include('spm_app.urls', namespace='spm_api')),
              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
