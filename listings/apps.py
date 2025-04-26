from django.apps import AppConfig

# config for the listings app
class ListingsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'  # set default primary key field type
    name = 'listings'  # app name so django can identify the app
