from django.urls import path
from .views import *



urlpatterns = [
    
    path('shorten/',get_data), 
    path('get_url/',index), 
    
] 
 