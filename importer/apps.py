from django.apps import AppConfig

class ImporterConfig(AppConfig):
    name = 'importer'

    def ready(self):
        import importer.signals  