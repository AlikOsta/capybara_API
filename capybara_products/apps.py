from django.apps import AppConfig


class CapybaraProductsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'capybara_products'
    verbose_name = 'Products'

    def ready(self):
        import capybara_products.signals  
