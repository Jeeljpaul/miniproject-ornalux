from django.contrib import admin
from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.index),
    path('base_home/',views.base),
    path('login/',views.login, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('adminhome/',views.adminhome),
    path('staffhome/',views.staffhome),
    path('register/',views.register, name='register'),
    path('forgot_password/', views.forgot_password),
    path('reset-password/<str:token>/', views.reset_password),
    path('social-auth/', include('social_django.urls', namespace='social')),

    # path('adminhome/add_p/', views.add_p, name='add_p'),
    path('adminhome/update_pro/<int:product_id>/', views.update_pro, name='update_pro'),  # New URL pattern
   
    # path('adminhome/add_product/', views.add_product, name='add_product'),
    path('adminhome/product_list/', views.product_list, name='product_list'),  # Make sure this line exists   
    path('adminhome/view_products/',views.view_products, name='view_products'),
    path('product_details/<int:product_id>/', views.product_details, name='product_details'),
    path('product/<int:product_id>/toggle_status/', views.toggle_product_status, name='toggle_product_status'),
    # path('product/<int:product_id>/update/', views.update_product, name='update_product'),

    path('adminhome/add-category/', views.add_category, name='add_category'),
    path('categories/', views.view_categories, name='view_categories'),
    path('add_attribute/<int:category_id>/', views.add_attribute_to_category, name='add_attribute_to_category'),


    path('get_category_attributes/<int:category_id>/', views.get_category_attributes, name='get_category_attributes'),
    path('adminhome/add_metaltype/', views.add_metaltype, name='add_metaltype'),
    path('view-metaltypes/', views.view_metaltypes, name='view_metaltypes'),
    path('adminhome/add_stonetype/', views.add_stonetype, name='add_stonetype'),
    path('view-stonetypes/', views.view_stonetypes, name='view_stonetypes'),

    path('adminhome/add_pro/', views.add_pro, name='add_pro'),


    path('view_registered_users/', views.view_registered_users, name='view_registered_users'),
    path('toggle_user_status/<int:user_id>/', views.toggle_user_status, name='toggle_user_status'),

    path('add_staff/', views.add_staff, name='add_staff'),
    path('view_staff/', views.view_staff, name='view_staff'),
    path('update_staff/<int:staff_id>/', views.update_staff, name='update_staff'),
    path('staff/delete/<int:staff_id>/', views.delete_staff, name='delete_staff'),


    path('product/', views.product, name='product'),
    path('ring_list/', views.ring_lists, name='ring_list'),
    path('earring_list/', views.earring_list, name='earring_list'),
    path('bracelet_list/', views.bracelet_lists, name='bracelet_list'),
    path('ring_detail/<int:product_id>/', views.ring_detail, name='ring_detail'),
    path('earring/<int:product_id>/', views.earring_detail, name='earring_detail'),
    path('bracelet_detail/<int:product_id>/', views.bracelet_detail, name='bracelet_detail'),
    path('allproducts',views.all_products,name='allproducts'),
    path('detail/<int:product_id>/', views.detail, name='detail'),
    path('book_schedule/<int:product_id>/', views.book_schedule, name='book_schedule'),
    path('submit_schedule/<int:product_id>/', views.submit_schedule, name='submit_schedule'),
    path('booking-details/<int:booking_id>/', views.booking_details, name='booking_details'),






    path('add_to_cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('view_cart/', views.view_cart, name='view_cart'),
    path('update_cart_quantity/', views.update_cart_quantity, name='update_cart_quantity'),
    path('remove_item_from_cart/', views.remove_item_from_cart, name='remove_item_from_cart'),
    path('add_to_wishlist/<int:product_id>/', views.add_to_wishlist, name='add_to_wishlist'),
    path('wishlist/', views.view_wishlist, name='view_wishlist'),
    path('remove_from_wishlist/<int:item_id>/', views.remove_from_wishlist, name='remove_from_wishlist'),

 

]
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)