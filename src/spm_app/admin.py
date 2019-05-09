from django.contrib import admin
from .models import *


class CustomPhotoDataAdmin(admin.ModelAdmin):
    """
    custom admin display to add read-only field to admin
    """
    readonly_fields = ('record_updated',)


admin.site.register(PhotoTag)
admin.site.register(PhotoData, CustomPhotoDataAdmin)
