# /home/thuytt/project_chat/project_chat/views.py
from django.shortcuts import render
from django.http import HttpResponse

def home(request):
    return render(request, 'chat/home.html')

def client1(request):
    return render(request, 'chat/client1.html')

def admin_view(request):
    return render(request, 'chat/admin.html')
