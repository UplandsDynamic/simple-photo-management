import logging
from django.contrib.auth.models import User, Group
from django.core.exceptions import ValidationError
from rest_framework import serializers
from datetime import datetime
from django.contrib.auth.password_validation import validate_password
from . import custom_validators
from django.db import IntegrityError
from django.utils.translation import gettext_lazy as _
from .models import PhotoTag, PhotoData
import uuid

# Get an instance of a logger
logger = logging.getLogger('django')


class UserSerializer(serializers.HyperlinkedModelSerializer):
    """
    note: because photo_data is a reverse relationship on the User model,
    it will not be included by default when using the ModelSerializer class,
    so we needed to add an explicit field for it.
    """
    photo_data = serializers.HyperlinkedRelatedField(
        many=True, view_name='photo_data-detail', read_only=True,
        lookup_field='pk')  # auto generated view_name is model name + '-detail'.

    class Meta:
        model = User
        fields = ('id', 'url', 'username', 'email', 'groups', 'photo_data')


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ('url', 'name')


class ChangePasswordSerializer(serializers.HyperlinkedModelSerializer):
    """
    Serializer for password change endpoint. Note: self.instance is the user object for the
    requester (ModelViewSet (in views.py) sets queryset as User model objects, and grabs
    the correct instance to update from the user ID passed as a URL path param.
    """

    """
    define the extra incoming "non-model" fields.
    """
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password',
                  'old_password', 'new_password')

    """
    field validations (in the form validate_a_custom_field)
    """

    def validate_old_password(self, value):
        # validate it is a real, acceptable pw
        validate_password(value, user=self.instance)
        return value

    def validate_new_password(self, value):
        validate_password(value, user=self.instance)
        return value

    """
    update method
    """

    def update(self, instance, validated_data):
        """
        overwrite update method if need to do extra stuff pre-save
        """

        """
        custom validations
        """
        try:
            custom_validators.validate_passwords_different(
                [validated_data['old_password'], validated_data['new_password']]
            )  # check old & new different

            custom_validators.validate_password_correct(user=instance,  # check old is valid
                                                        value=validated_data['old_password'])
        except (ValidationError, KeyError) as e:
            raise serializers.ValidationError(f'Error: {e}')

        instance.set_password(validated_data['new_password'])
        instance.save()
        # remove password from instance, replaced with 'CHANGED' str (for client ref) & return the instance as response
        instance.password = 'CHANGED'
        return instance


class PhotoDataSerializer(serializers.HyperlinkedModelSerializer):
    """
    PhotoData serializer
    """

    """
    Any special attributes to add to fields (e.g. if want to make it read-only)
    """

    tag_qs = PhotoTag.objects.all()

    owner = serializers.ReadOnlyField(source='owner.username')
    id = serializers.ReadOnlyField()
    tags = serializers.SlugRelatedField(
        many=True,
        slug_field='tag',
        queryset=PhotoTag.objects.all())

    """
    Any custom fields (non-model)
    FYI, details of how to process a non-model field in the request, here: https://stackoverflow.com/a/37718821
    """

    # return staff status of requester
    user_is_admin = serializers.SerializerMethodField(
        method_name='administrators_check')

    # add UUID to ensure caches can be cleared for new img
    uuid = serializers.SerializerMethodField(method_name='generate_uuid')

    def generate_uuid(self, obj):
        return uuid.uuid4().hex

    def administrators_check(self, obj):
        return self.context['request'].user.groups.filter(name='administrators').exists()

    # return request datetime
    datetime_of_request = serializers.SerializerMethodField(
        method_name='create_request_time')

    def create_request_time(self, obj):
        # return datetime.utcnow().strftime('%d %b %Y, %H:%M:%S UTC')
        return datetime.utcnow()

    class Meta:
        model = PhotoData
        fields = ('id', 'owner', 'file_name', 'file_format', 'tags', 'user_is_admin',
                  'datetime_of_request', 'record_updated', 'public_img_url', 'public_img_tn_url', 'original_url', 'uuid')

    """
    Additional validations. 
    Data param is dict of unvalidated fields.
    Note, model validations are passed as validators to serializer validation, so
    most validation here is done on the model.
    Non-model fields may be validated here.
    """

    def validate(self, data):
        logger.info('Running clean on serializer')
        """
        extra validations for non-model fields
        """
        # no non-model fields to validate.
        return data

    """
    create or update
    """

    def create(self, validated_data):
        """
        overwrite create method if need to do extra stuff pre-save
        """

        """
        Only admins are allowed to create new objects
        """
        if not self.administrators_check(self):
            raise serializers.ValidationError(
                detail=f'Record creation denied for this user level')
        try:
            super().create(validated_data)  # now call parent method to do the save
            return self.validated_data
        except IntegrityError as i:
            raise serializers.ValidationError(detail=f'{i}')

    def update(self, instance, validated_data):
        """
        overwrite update method if need to do extra stuff pre-save
        """
        # call parent method to do the update
        return super().update(instance, validated_data)
        # return the updated instance


class PhotoTagSerializer(serializers.HyperlinkedModelSerializer):
    """
    PhotoTag serializer
    """

    """
    Any special attributes to add to fields (e.g. if want to make it read-only)
    """

    owner = serializers.ReadOnlyField(source='owner.username')
    id = serializers.ReadOnlyField()

    """
    Any custom fields (non-model)
    FYI, details of how to process a non-model field in the request, here: https://stackoverflow.com/a/37718821
    """

    # return staff status of requester
    user_is_admin = serializers.SerializerMethodField(
        method_name='administrators_check')

    def administrators_check(self, obj):
        return self.context['request'].user.groups.filter(name='administrators').exists()

    # return request datetime
    datetime_of_request = serializers.SerializerMethodField(
        method_name='create_request_time')

    def create_request_time(self, obj):
        # return datetime.utcnow().strftime('%d %b %Y, %H:%M:%S UTC')
        return datetime.utcnow()

    class Meta:
        model = PhotoTag
        fields = ('id', 'tag', 'datetime_of_request', 'user_is_admin', 'owner')

    """
    Additional validations. 
    Data param is dict of unvalidated fields.
    Note, model validations are passed as validators to serializer validation, so
    most validation here is done on the model.
    Non-model fields may be validated here.
    """

    def validate(self, data):
        logger.info('Running clean on serializer')
        """
        extra validations for non-model fields
        """
        # no non-model fields to validate.
        return data

    """
    create or update
    """

    def create(self, validated_data):
        """
        overwrite create method if need to do extra stuff pre-save
        """

        """
        Only superusers are allowed to create new objects
        """
        if not self.administrators_check(self):
            raise serializers.ValidationError(
                detail=f'Record creation denied for this user level')
        # remove units_to_transfer write_only (non-model) field for the create() method (only for updates)
        if 'units_to_transfer' in validated_data:
            del validated_data['units_to_transfer']
        try:
            super().create(validated_data)  # now call parent method to do the save
            return self.validated_data
        except IntegrityError as i:
            raise serializers.ValidationError(detail=f'{i}')

    def update(self, instance, validated_data):
        """
        overwrite update method if need to do extra stuff pre-save
        """
        # call parent method to do the update
        super().update(instance, validated_data)
        # return the updated instance
        return instance
