from django.contrib import admin
from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.index),
    path('base_home/',views.base),
    path('login/',views.login),
    path('logout/', views.logout_view, name='logout'),
    path('adminhome/',views.adminhome),
    path('staffhome/',views.staffhome),
    path('register/',views.register),
    path('forgot_password/', views.forgot_password),
    path('reset-password/<str:token>/', views.reset_password),


    path('adminhome/add_p/', views.add_p, name='add_p'),
    path('update_p/<int:product_id>/', views.update_p, name='update_p'),  # New URL pattern
   
    path('adminhome/add_product/', views.add_product, name='add_product'),
    path('adminhome/product_list/', views.product_list, name='product_list'),  # Make sure this line exists   
    path('adminhome/view_products/',views.view_products, name='view_products'),
    path('product_details/<int:product_id>/', views.product_details, name='product_details'),
    path('product/<int:product_id>/toggle_status/', views.toggle_product_status, name='toggle_product_status'),
    path('product/<int:product_id>/update/', views.update_product, name='update_product'),

    path('view_registered_users/', views.view_registered_users, name='view_registered_users'),
    path('toggle_user_status/<int:user_id>/', views.toggle_user_status, name='toggle_user_status'),

    path('add_staff/', views.add_staff, name='add_staff'),
    path('view_staff/', views.view_staff, name='view_staff'),
    path('update_staff/<int:staff_id>/', views.update_staff, name='update_staff'),
    path('staff/delete/<int:staff_id>/', views.delete_staff, name='delete_staff'),


]
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)