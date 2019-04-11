import logging
from django.contrib.auth.models import User, Group
from django.http import JsonResponse
from django.utils.datetime_safe import datetime
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
from django.conf import settings

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
    def add_record_to_db(record, owner, resync_tags=False):
        """
        method to add images to the database model
        :param record: dict of saved conversion data and tags: e.g.:
            {conversion_data: {'orig_path': '/path/to/orig/image', 'processed_path':'/path/to/processed_image',
            'filename': '4058.jpeg'}, tag_data: {'iptc_key': 'Iptc.Application2.Keywords', 'tags':
            ['DATE: 1974', 'PLACE: The Moon']}
        :param owner: current user
        :param resync_tags: whether to resync embedded IPTC tags from image file to the PhotoData model
        :return: saved record | False
        """
        # TODO ... TEST SEARCH ...
        try:
            updated_tags = []
            try:
                filename = record['conversion_data']['filename']
                original_path = record['conversion_data']['orig_path']
                processed_path = record['conversion_data']['processed_path']
                logger.info(f'FILENAME: {filename}')
                photo_data_record, new_record_created = PhotoData.objects.update_or_create(
                    file_name=os.path.splitext(filename)[0],
                    defaults={
                        'owner': owner,
                        'file_format': os.path.splitext(filename)[1],
                        'original_url': os.path.join(original_path, filename),
                        'processed_url': os.path.join(processed_path, filename)})
            except Exception as e:
                new_record_created = False
                photo_data_record = None
                logger.error(f'An exception occurred whilst saving image data to the database: {e}')
            """
            if new image data was created - or resync_tags=True - , create PhotoTag objects 
            (creating in the model if necessary with update_or_create), then populate saved 
            PhotoData model's M2M tags field with that list. Then, add image data to a list for return.
            """
            if photo_data_record and record['tag_data']['tags'] and (new_record_created or resync_tags):
                for tag in record['tag_data']['tags']:
                    try:
                        tag, tag_created = PhotoTag.objects.get_or_create(tag=tag, owner=owner)
                        updated_tags.append(tag)
                    except Exception as e:
                        logger.warning(f'An exception occurred whilst attempting to save tags to database: {e}')
                # save tags to PhotoData model
                photo_data_record.tags.set(updated_tags)
                photo_data_record.record_updated = datetime.utcnow()
                # save the model
                photo_data_record.save()
                logger.info(f'Added record: {photo_data_record}')
                return photo_data_record
        except Exception as e:
            logger.warning(f'An exception occurred whilst attempting to save photos to database: {e}')
        return False

    @staticmethod
    def process_images(retag=False, user=None, add_record_to_db=None):
        """
        method to process images (make resized copy (i.e. a 'processed' copy) & copy tags from original to resized)
        :param retag: whether to re-copy over tags from original to processed image, if filename already exists
        :param user: current user
        :param add_record_to_db: function, that submits records to DB model
        :return: True | False
        """
        original_image_path = settings.SPM['ORIGINAL_IMAGE_PATH']
        processed_image_path = settings.SPM['PROCESSED_IMAGE_PATH']
        conversion_format = settings.SPM['CONVERSION_FORMAT']
        try:
            retag = RequestQueryValidator.validate('bool', retag)
            # initiate a ProcessImages object
            image_processor = ProcessImages(image_path=original_image_path,
                                            processed_image_path=processed_image_path,
                                            conversion_format=conversion_format,
                                            retag=retag)
            # get reference to the generator that processes images
            process_images_generator = image_processor.generate_processed_copies()
            if process_images_generator:
                # iterate generator & pass records to function that submits them to DB model
                """
                # debug: test iterating generated values, one at a time
                iterator = iter(process_images_generator)
                print(next(iterator))
                print(next(iterator))
                """
                for processed_record in process_images_generator:
                    async_task(add_record_to_db, record=processed_record, owner=user, resync_tags=retag)
            else:
                logger.error(f'An error occurred during image processing. Operation cancelled.')
                return False
            return True
        except (ValidationError, Exception) as e:
            if isinstance(e, ValidationError):
                logger.error(f'Validation error: {e.message}')
            else:
                logger.error(f'Error in processing: {e}')
        return False

    def get(self, request):
        """
        hand off the image processing and tagging task to django_q multiprocessing (async)
        """
        async_task(AddTags.process_images, self.request.query_params.get('retag', None), self.request.user,
                   self.add_record_to_db)
        return JsonResponse({'Status': 'Processing .......'}, status=202)
