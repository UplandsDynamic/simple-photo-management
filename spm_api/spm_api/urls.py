from django.contrib import admin
from django.urls import path
from django.conf.urls import url, include, static

urlpatterns = [
    path('admin/', admin.site.urls),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^api/', include('spm_app.urls', namespace='spm_api')),
]