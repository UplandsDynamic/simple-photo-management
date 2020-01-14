from django.db import models
from rest_framework.authtoken.models import Token
from django.conf import settings
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from . import custom_validators
import logging

# Get an instance of a logger
logger = logging.getLogger('django')


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    """
    Signal receiver to automatically create auth token for new users.
    Placed here as needs to be imported and run by Django on startup,
    and all model.py modules are.
    """
    if created:
        Token.objects.create(user=instance)


@receiver(pre_save)
def clean_on_update(sender, instance=None, created=False, **kwargs):
    """
    if updating, run clean (not called by default if save() method invoked directly,
    such as when updating.
    """
    if sender == PhotoData:
        logger.info('About to clean on update ...')
        instance.full_clean()

class PhotoData(models.Model):
    record_created = models.DateTimeField(auto_now_add=True)
    record_updated = models.DateTimeField(auto_now=True)
    owner = models.ForeignKey(
        'auth.User', related_name='photo_data', on_delete=models.SET_NULL, null=True)
    file_name = models.CharField(max_length=100, blank=False, null=False, unique=True,
                                 validators=[custom_validators.validate_alphanumplus])
    file_format = models.CharField(max_length=100, blank=True, null=False,
                                   validators=[custom_validators.validate_alphanumplus])
    tags = models.ManyToManyField(
        'PhotoTag', related_name='photo_data', blank=True)
    original_url = models.CharField(max_length=255, blank=False, null=True, unique=True,
                                    validators=[custom_validators.validate_url])
    processed_url = models.CharField(max_length=255, blank=False, null=True, unique=True,
                                     validators=[custom_validators.validate_url])
    public_img_url = models.CharField(max_length=255, blank=False, null=False, unique=False,
                                      validators=[custom_validators.validate_url])
    public_img_tn_url = models.CharField(max_length=255, blank=False, null=False, unique=False,
                                         validators=[custom_validators.validate_url])
    mod_lock = models.BooleanField(null=False, default=False)

    class Meta:
        ordering = ('id', 'original_url')
        # indexes = [
        #     models.Index(fields=['file_name']),
        # ]

    def __str__(self):
        #return f'{self.file_name}{self.file_format}'
        return str(self.id)

    def clean(self):
        logger.info('Running clean on model')
        """
        clean method
        """

        """ Call clean """
        super(PhotoData, self).clean()

    def save(self, *args, **kwargs):
        """
        Any custom methods, filters etc to run before saving ...
        """
        # nothing custom to do here, move along ...
        super(PhotoData, self).save(*args, **kwargs)


class PhotoTag(models.Model):
    tag = models.CharField(unique=True, max_length=100, blank=True, null=False,
                           validators=[custom_validators.validate_alphanumplus])
    owner = models.ForeignKey(
        'auth.User', related_name='photo_tag', on_delete=models.SET_NULL, null=True)
    user_access = models.ManyToManyField('auth.User', related_name='user_access', blank=True)
    record_created = models.DateTimeField(auto_now_add=True)
    record_updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('tag',)
        indexes = [
            models.Index(fields=['tag'])
        ]

    def __str__(self):
        return self.tag

    def save(self, *args, **kwargs):
        """
        any custom methods to run before saving ...
        """
        # nothing custom to do ...
        super(PhotoTag, self).save(*args, **kwargs)
