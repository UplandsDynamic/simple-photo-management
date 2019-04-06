import logging
from django.contrib.auth.models import User, Group
from django.http import JsonResponse
from rest_framework.views import APIView
import os
from .custom_validators import RequestQueryValidator, validate_search
from django.core.exceptions import ValidationError
from rest_framework import (viewsets, permissions, serializers, status)
from .serializers import (
    UserSerializer,
    GroupSerializer,
    ChangePasswordSerializer,
    PhotoDataSerializer,
    PhotoTagSerializer
)
from .custom_permissions import AccessPermissions
from .models import PhotoData, PhotoTag
from django.db.models import Q
from rest_framework.decorators import action
from .spm_worker.process_images import ProcessImages
from django_q.tasks import async_task, result
from functools import partial

"""
Note about data object (database record):
Record referenced by URL param can be accessed in create & update methods through: self.get_object()

Note about permissions:
If viewset passed into class is ModelViewSet rather than a permission restricted one such as
ReadOnlyModelViewset, then permission classes can be set within the class,
via the 'permission_classes' class attribute.

Permissions classes include:
    Defaults: permissions.IsAuthenticated, permissions.IsAuthenticatedOrReadOnly, permissions.IsAdmin
    My custom: IsOwnerOrReadOnly

Need to be put in a set, e.g. permission_classes = (permissions.IsAuthenticated, IsOwnerOrReadOnly).
If only one, leave trailing comma e.g.(permissions.IsAuthentication,)
"""

# Get an instance of a logger
logger = logging.getLogger('django')


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoints for users
    """

    """
    Includes by default the ListCreateAPIView & RetrieveUpdateDestroyAPIView
    (i.e. provides users-list and users-detail views, accessed by path, & path/<id>).
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAdminUser,)  # overrides default perm level, set in settings.py


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = (permissions.IsAdminUser,)


class PasswordUpdateViewSet(viewsets.ModelViewSet):
    """
    API endpoint for updating password
    """
    queryset = User.objects.all()
    serializer_class = ChangePasswordSerializer
    permission_classes = (AccessPermissions,)
    lookup_field = 'username'

    def perform_update(self, serializer):
        """
        override perform_update to perform any additional filtering, modification, etc
        """
        super().perform_update(serializer)


class PhotoDataViewSet(viewsets.ModelViewSet):
    """
    API endpoints for PhotoData
    """

    """
    Includes by default the ListCreateAPIView & RetrieveUpdateDestroyAPIView
    i.e. provides photodata-list and photodata-detail views, accessed by path, & path/<id>)
    """
    queryset = PhotoData.objects.all()
    serializer_class = PhotoDataSerializer
    permission_classes = (AccessPermissions,)

    """
    Note on permissions:
    Access control is dealt with in 2 places: here (views.py) and serializers.py.

        - views.py: basic 1st hurdle checks, performed before input validation, 
        including whether requester user level has access to models, and whether has ability to 
        preform actions on model objects. This is via permission_classes 
        (may call access permissions classes from ./custom_permissions.py or default access permission 
        classes from DRF.

        - serializers.py: 2nd hurdle checks - more complicated checks performed after input validation 
        but before changes committed to the model. E.g. ensuring only certain user levels are able 
        to update specific fields in certain ways.    
    """

    def get_queryset(self):
        # order queryset using request query (or 'id' by default if no order_by query)
        records = self.queryset.order_by(RequestQueryValidator.validate(
            RequestQueryValidator.order_by, self.request.query_params.get('order_by', None)
        ))
        # set username of requester to user attr of serializer to allow return admin status in response
        self.serializer_class.user = self.request.user
        # if searching for a product by description
        try:
            if 'tag' in self.request.query_params and self.request.query_params.get('tag', None):
                search_query = validate_search(self.request.query_params.get('tag'))
                records = records.filter(Q(tags__icontains=search_query) | Q(tags__icontains=search_query)
                                         if search_query else None)
        except ValidationError as e:
            # if invalid search char, don't return error response, just return empty
            logger.info(f'Returning no results in response because: {e}')
            records = []
        return records  # return everything

    def perform_create(self, serializer_class):
        """
        override perform_create to save the user as the owner of the record
        """
        serializer_class.save(owner=self.request.user)

    def perform_update(self, serializer):
        """
        override perform_update to perform any additional filtering, modification, etc
        """
        super().perform_update(serializer)  # call to parent method to save the update

    def perform_destroy(self, instance):
        # only allow admins to delete objects
        if self.request.user.groups.filter(name='administrators').exists():
            super().perform_destroy(instance)
        else:
            raise serializers.ValidationError(detail='You are not authorized to delete photo data!')


class PhotoTagViewSet(viewsets.ModelViewSet):
    """
    API endpoints for PhotoTag
    """

    """
    Includes by default the ListCreateAPIView & RetrieveUpdateDestroyAPIView
    i.e. provides phototag-list and phototag-detail views, accessed by path, & path/<id>)
    """
    queryset = PhotoTag.objects.all()
    serializer_class = PhotoTagSerializer
    permission_classes = (AccessPermissions,)

    """
    Note on permissions:
    Access control is dealt with in 2 places: here (views.py) and serializers.py.

        - views.py: basic 1st hurdle checks, performed before input validation, 
        including whether requester user level has access to models, and whether has ability to 
        preform actions on model objects. This is via permission_classes 
        (may call access permissions classes from ./custom_permissions.py or default access permission 
        classes from DRF.

        - serializers.py: 2nd hurdle checks - more complicated checks performed after input validation 
        but before changes committed to the model. E.g. ensuring only certain user levels are able 
        to update specific fields in certain ways.    
    """

    def get_queryset(self):
        # order queryset using request query (or 'id' by default if no order_by query)
        records = self.queryset.order_by(RequestQueryValidator.validate(
            RequestQueryValidator.order_by, self.request.query_params.get('order_by', None)
        ))
        # set username of requester to user attr of serializer to allow return admin status in response
        self.serializer_class.user = self.request.user
        # if searching for a product by description
        try:
            if 'tag' in self.request.query_params and self.request.query_params.get('tag', None):
                search_query = validate_search(self.request.query_params.get('tag'))
                records = records.filter(Q(tags__icontains=search_query) | Q(tags__icontains=search_query)
                                         if search_query else None)
        except ValidationError as e:
            # if invalid search char, don't return error response, just return empty
            logger.info(f'Returning no results in response because: {e}')
            records = []
        return records  # return everything

    def perform_create(self, serializer_class):
        """
        override perform_create to save the user as the owner of the record
        """
        serializer_class.save(owner=self.request.user)

    def perform_update(self, serializer):
        """
        override perform_update to perform any additional filtering, modification, etc
        """
        super().perform_update(serializer)  # call to parent method to save the update

    def perform_destroy(self, instance):
        # only allow admins to delete objects
        if self.request.user.groups.filter(name='administrators').exists():
            super().perform_destroy(instance)
        else:
            raise serializers.ValidationError(detail='You are not authorized to delete photo data!')


class AddTags(APIView):
    """
    API endpoint that allows tags to be read from photos
    and added to the database
     """

    permission_classes = (permissions.IsAuthenticated,)

    def __init__(self):
        super().__init__()

    @staticmethod
    def add_tags_to_db(photo_tag_model, tags, owner):
        """
        method to add tags to the database model
        :param photo_tag_model: the PhotoTag database model
        :param tags: list of tag dicts: [{'path': path/to/file, 'filename': filename, 'iptc_key': IPTC key name,
        'tags': ['tag1', 'tag2']}]
        :param owner: user who is submitting the tags
        :return: list of added tags | []
        """
        added_tags = []
        for tag_record in tags:
            for tag in tag_record['tags']:
                try:
                    tag_instance = photo_tag_model()
                    tag_instance.tag = tag
                    tag_instance.owner = owner
                    tag_instance.save()
                    added_tags.append(tag)
                except Exception as e:
                    logger.warning(f'An exception occurred whilst attempting to save tags to database: {e}')
        return added_tags

    @staticmethod
    def add_images_to_db():
        """
        method to add images to the database model
        :return: list of added images | []
        """
        pass
        # {'conversions': [{'path': '/path/to/processed/image', 'filename': '4058.jpeg'}],
        # 'tags': [{'path': '/path/to/tagged/image','4058.tif','Iptc.Application2.Keywords',
        # 'tags': ['DATE: 1974','PLACE: The Moon']}]}

    @staticmethod
    def process_images(reconvert=False, retag=False, user=None, add_tags_to_db=None):
        """
        method to process images (make resized copy (i.e. a 'processed' copy) & copy tags from original to resized)
        :param reconvert: whether to reconvert if file name already exists
        :param retag: whether to re-copy over tags from original to processed image, if filename already exists
        :param user: current uses
        :param add_tags_to_db:
        :return: True | False
        """
        original_image_path = os.path.normpath(os.path.normpath(f'{os.path.join(os.getcwd(), "../test_images")}'))
        processed_image_path = os.path.normpath(
            os.path.normpath(f'{os.path.join(os.getcwd(), "../test_images/processed")}'))
        conversion_format = 'jpeg'
        try:
            reconvert = RequestQueryValidator.validate('bool', reconvert)
            retag = RequestQueryValidator.validate('bool', retag)
            processed = ProcessImages(image_path=original_image_path,
                                      processed_image_path=processed_image_path,
                                      conversion_format=conversion_format,
                                      reconvert=reconvert,
                                      retag=retag).main()
            # save data
            if processed.get('tags'):
                added_tags = add_tags_to_db(photo_tag_model=PhotoTag, tags=processed.get('tags'),
                                            owner=user)
                logger.info(f'Added tags: {added_tags}')
            return True
        except (ValidationError, Exception) as e:
            logger.error(f'Validation error: {e.message if isinstance(e, ValidationError) else e}')
        return False

    def get(self, request):
        """
        hand off the image processing and tagging task to django_q multiprocessing (async)
        """
        async_task(AddTags.process_images, self.request.query_params.get('reconvert', None),
                   self.request.query_params.get('retag', None), self.request.user, self.add_tags_to_db)
        return JsonResponse({'Status': 'Processing .......'}, status=202)
