from django.contrib import admin
from django.apps import apps

# Register models for applications
app_models = apps.get_app_config("shemsAccount").get_models()
for model in app_models:
    try:
        admin.site.register(model)
    except admin.sites.AlreadyRegistered:
        pass

acct_models = apps.get_app_config("shemsWebapp").get_models()
for model in acct_models:
    try:
        admin.site.register(model)
    except admin.sites.AlreadyRegistered:
        pass
