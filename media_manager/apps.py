from django.apps import AppConfig


class MediaManagerConfig(AppConfig):
    name = "media_manager"

    def ready(self):
        import media_manager.signals  # noqa: F401
