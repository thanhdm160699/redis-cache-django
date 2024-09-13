from django.shortcuts import render

# Create your views here.
# myproject/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),  # Đăng nhập vào trang quản trị Django
    path('api/', include('myapp.urls')),  # Bao gồm các URL từ ứng dụng `myapp`
]