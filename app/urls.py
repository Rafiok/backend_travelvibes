from django.urls import path
from .views import *

urlpatterns = [
    path('charge_file/', charge_file)
]