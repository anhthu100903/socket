from django.contrib import admin
from django.urls import path
from chat import views

urlpatterns = [
    path('', views.home, name='home'),  
  
    path('admin-chat/', views.admin_view, name='admin_chat'),

    path('client1/', views.client1, name='client1'),
]
