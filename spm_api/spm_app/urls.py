from django.conf.urls import url, include
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
# router.register(r'stock', views.StockDataViewSet)  # define manually to allow DRF unit testing (router testing buggy)
# router.register(r'change-password', views.PasswordUpdateViewSet)  # define manually below to allow dots in usernames

"""
set up the url patterns for the functional views and simple class based views
Note: Mapping for actions (used in as_view), are:
    {
    'get': 'retrieve'  # to retrieve one object, as spec by pk passed in url param, e.g. /stock/1
    'get': 'list' # to list all objects, e.g. /stock/
    'get': 'latest' # CUSTOM action (defined in views.StockDataViewSet.latest(), routed /api/v1/stock/latest/ (below)).
    'post': 'create'
    'put': 'update',
    'patch': 'partial_update',
    'patch': 'custom_update', # CUSTM ACTION
    'patch': 'perform_single_update', # CUSTM ACTION
    'patch': 'perform_bulk_partial_update',  # CUSTOM ACTION
    'delete': 'destroy',
    }
"""
functional_view_urlpatterns = [
    url('^v2/change-password/(?P<username>[a-zA-Z0-9.].+)/$',
        views.PasswordUpdateViewSet.as_view(
            {'patch': 'partial_update'})),
    url(r'^v2/logout/$', views.Logout.as_view()),
    url('^v2/tags/$', views.PhotoTagViewSet.as_view(
        {'get': 'list', 'post': 'create', 'patch': 'partial_update'}), name='photo_tag'),
    url('^v2/tags/(?P<pk>\d+)/$', views.PhotoTagViewSet.as_view(
        {'get': 'retrieve', 'patch': 'partial_update', 'delete': 'destroy', 'put': 'update'}), name='photo-tag_detail'),
    url('^v2/photos/$', views.PhotoDataViewSet.as_view(
        {'get': 'list'}), name='photo_data'),
    url('^v2/photos/(?P<pk>\d+)/$', views.PhotoDataViewSet.as_view(
        {'get': 'retrieve', 'patch': 'perform_update', 'delete': 'destroy', 'put': 'update'}),
        name='photo_data-detail'),
    url('^v2/process_photos', views.ProcessPhotos.as_view()),
    # url('^v2/stock/latest/$', views.StockDataViewSet.as_view(
    #     {'get': 'latest'})),
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
    url(r'^(/?)$', schema_view),
    url(r'^api-token-auth/', authviews.obtain_auth_token),
    url(r'^schema(/?)$', schema_view),
]
