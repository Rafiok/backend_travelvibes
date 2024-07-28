from django.urls import path
from .views import *

urlpatterns = [
    path('charge_file/', charge_file),
    path('register_user/', register_user),
    path('get_voyages/', get_voyages),
    path('search_place/<str:name>/', search_place, name="search_place"),
    path('get_details/', get_details),
    path('create_voyage/', create_voyage),
    path('create_dem/', create_dem),
    path('get_requetes/', get_requetes),
    path('init_chat/<int:pk>/', init_chat),
    path('set_decision/', set_decision),
    path('charg_files/', charg_files),
    path('init_portefeuille/', init_portefeuille),
    path('create_transaction/', create_transaction),
    path('ping/', ping)
]