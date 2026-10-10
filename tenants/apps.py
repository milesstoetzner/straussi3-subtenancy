from django.apps import AppConfig

class Config(AppConfig):
    name = 'tenants'
    verbose_name = 'Haupt-/Untermieter'
    verbose_name_plural = 'Haupt-/Untermieter'

    def ready(self):
        from tenants import signals  # noqa: F401  (connects the auth logging receivers)
