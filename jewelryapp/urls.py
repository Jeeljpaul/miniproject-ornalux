from django.contrib import admin
from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.index),
    path('base_home/',views.base),
    path('login/',views.login),
    path('adminhome/',views.adminhome),
    path('staffhome/',views.staffhome),
    path('register/',views.register),
    path('forgot_password/', views.forgot_password),
    path('reset-password/<str:token>/', views.reset_password)
]
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)