from django.urls import re_path
from rest_framework import routers, permissions
from rest_framework.urlpatterns import format_suffix_patterns
from . import views
from rest_framework.schemas import get_schema_view
from rest_framework.authtoken import views as authviews

app_name = 'spm_app'

"""
set up the routers for the viewset class based views
"""
# router = routers.DefaultRouter()
# router.register(r'users', views.UserViewSet)
# router.register(r'groups', views.GroupViewSet)
# router.register(r'change-password', views.PasswordUpdateViewSet)  # define manually below to allow dots in usernames

"""
set up the url patterns for the functional views and simple class based views
Note: Mapping for actions (used in as_view), are:
    {
    'get': 'retrieve'  # to retrieve one object, as spec by pk passed in url param
    'get': 'list' # to list all objects
    'get': 'prune' # to run pune function (PhotoTags)
    'get': 'latest' # CUSTOM action (defined in views.StockDataViewSet.latest()
    'post': 'create'
    'put': 'update',
    'patch': 'partial_update',
    'patch': 'custom_update', # CUSTOM ACTION
    'patch': 'perform_single_update', # CUSTOM ACTION
    'patch': 'perform_bulk_partial_update',  # CUSTOM ACTION
    'delete': 'destroy',
    }
"""
functional_view_urlpatterns = [
    re_path('^v2/change-password/(?P<username>[a-zA-Z0-9.].+)/$',
        views.PasswordUpdateViewSet.as_view(
            {'patch': 'partial_update'})),
    re_path(r'^v2/logout/$', views.Logout.as_view()),
    re_path('^v2/tags/prune/$', views.PhotoTagViewSet.as_view(
        {'delete': 'prune_tags'}), name='photo_tag_prune'),
    re_path('^v2/tags/$', views.PhotoTagViewSet.as_view(
        {'get': 'list', 'post': 'create', 'patch': 'partial_update'}), name='photo_tag'),
    re_path('^v2/tags/(?P<pk>\d+)/$', views.PhotoTagViewSet.as_view(
        {'get': 'retrieve', 'patch': 'partial_update', 'delete': 'destroy', 'put': 'update'}), name='photo-tag_detail'),
    re_path('^v2/photos/$', views.PhotoDataViewSet.as_view(
        {'get': 'list'}), name='photo_data'),
    re_path('^v2/photos/(?P<pk>\d+)/$', views.PhotoDataViewSet.as_view(
        {'get': 'retrieve', 'patch': 'perform_update', 'delete': 'destroy'}),
        name='photo_data-detail'),
    re_path('^v2/process_photos', views.ProcessPhotos.as_view()),
]

"""
add in extra urls to provide option to add content type suffix to requests 
(as handled by the api_view wrapper, in views.py)
"""
urlpatterns = format_suffix_patterns(functional_view_urlpatterns)

"""
set up schema
"""
schema_view = get_schema_view(
    title='Simple Photo Management API',
    # not public api, so only allow admin to view the schema
    permission_classes=[permissions.IsAdminUser]
)

# final url patterns (everything included)
urlpatterns += [
    re_path(r'^(/?)$', schema_view),
    re_path(r'^api-token-auth/', authviews.obtain_auth_token),
    re_path(r'^schema(/?)$', schema_view),
]
