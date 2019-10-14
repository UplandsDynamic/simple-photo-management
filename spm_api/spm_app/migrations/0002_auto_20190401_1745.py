# Generated by Django 2.1.8 on 2019-04-01 17:45

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('spm_app', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='phototag',
            name='owner',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='photo_tag', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='phototag',
            name='record_created',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='phototag',
            name='record_updated',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
