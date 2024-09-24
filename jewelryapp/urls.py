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
    path('adminhome/view_products/',views.view_products, name='view_products'),
    path('view_product_details/<int:product_id>/', views.view_product_details, name='view_product_details'),
    path('delete_product/<int:product_id>/', views.delete_product, name='delete_product'),
    path('update_product/<int:product_id>/', views.update_product, name='update_product'),
    path('view_registered_users/', views.view_registered_users,),
    path('delete_user/<int:user_id>/', views.delete_user, name='delete_user'),

]
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)