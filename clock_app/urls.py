from django.urls import path, re_path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('category/<str:name>', views.category, name='category'),
    path('singal_product/<int:product_id>', views.singal_product, name='singal_product'),
    path('category_brand/<str:name>/<str:brand>', views.category_brand, name='category_brand'), 
    path('category_brand_only/<str:brand>', views.category_brand_only, name='category_brand_only'),  
    path('add_to_cart/<int:product_id>/', views.add_to_cart, name="add_to_cart"),
    path('cart_view/', views.cart_view, name='cart_view'),
    path('update_cart/<int:product_id>/<str:action>/', views.update_cart, name="update_cart"),
    path('remove_from_cart/<int:product_id>/', views.remove_from_cart, name="remove_from_cart"),
    path('search_data/', views.search_page, name='search_data'),
    # path('category_brand_only/<str:brand>', views.category_brand_only, name='category_brand_only'), 
    path('login/', views.login_user, name="login"),
    path('logout/', views.logout_user, name="logout_user"),
    path('register/', views.register, name='register'),
    path("account/", views.account, name="account"),
    path('wishlist_view/', views.wishlist_view, name='wishlist_view'),
    path('add_to_wishlist/<int:product_id>/', views.add_to_wishlist, name='add_to_wishlist'),
    path('remove_from_wishlist/<int:product_id>/', views.remove_from_wishlist, name='remove_from_wishlist'),

    path('checkout/', views.checkout, name='checkout'),
    path("payment-success/", views.payment_success, name="payment_success"),
    path("payment-cancel/", views.payment_cancel, name="payment_cancel"),
    
    # Admin Panel
    path('custom-admin/login/', views.admin_login, name='admin_login'),
    path('custom-admin/logout/', views.logout_admin, name="logout_admin"),
    path('custom-admin/', views.admin_dashboard, name='admin_dashboard'),
    # Category URLs
    path('custom-admin/categories/', views.category_list, name='category_list'),
    path('custom-admin/category/add/', views.add_category, name='add_category'),
    path('custom-admin/category/update/<int:id>/', views.update_category, name='update_category'),
    path('custom-admin/category/delete/<int:id>/', views.delete_category, name='delete_category'),

    # Brand URLs
    path('custom-admin/brands/', views.brand_list, name='brand_list'),
    path('custom-admin/brand/add/', views.add_brand, name='add_brand'),
    path('custom-admin/brand/update/<int:id>/', views.update_brand, name='update_brand'),
    path('custom-admin/brand/delete/<int:id>/', views.delete_brand, name='delete_brand'),
    # Product Admin URLs
    path('custom-admin/products/', views.admin_product_list, name='admin_product_list'),
    path('custom-admin/product/detail/<int:id>/', views.admin_product_detail, name='admin_product_detail'),
    path('custom-admin/product/add/', views.add_product, name='add_product'),
    path('custom-admin/product/update/<int:id>/', views.update_product, name='update_product'),
    path('custom-admin/product/delete/<int:id>/', views.delete_product, name='delete_product'),
    
    # Customer Orders Management URLs
    path('custom-admin/orders/', views.admin_order_list, name='admin_order_list'),
    path('custom-admin/order/detail/<int:id>/', views.admin_order_detail, name='admin_order_detail'),
    
    # re_path(r'^.*$', views.redirect_to_home),
    
] 
