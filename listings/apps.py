from django.apps import AppConfig



class ListingsConfig(AppConfig):
    name = 'listings'
from django.apps import AppConfig

class ListingsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'listings'

    def ready(self):
        # 🔧 NEW: Imports and mounts your automated cleanup signal loop on system boot
        import listings.signals