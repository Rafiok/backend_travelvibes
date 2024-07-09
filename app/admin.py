from django.contrib import admin
from django.apps import apps
from .models import *

models = apps.get_models()

for model in models : 
    if str(model) != "<class 'fcm_django.models.FCMDevice'>" :
        try : 
            admin.site.register(model)
        except :
            pass

# Register your models here.

