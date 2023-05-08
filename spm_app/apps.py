from django.apps import AppConfig


class SpmConfig(AppConfig):
    name = 'spm_app'

    def ready(self):
        from spm_app import signals