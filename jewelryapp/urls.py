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
    path('reset-password/<str:token>/', views.reset_password),
    path('adminhome/add_product/', views.add_product),
    path('adminhome/view_products/',views.view_products),
    path('view_product_details/<int:product_id>/', views.view_product_details),
    path('delete_product/<int:product_id>/', views.delete_product),
]
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)