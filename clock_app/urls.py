from django.urls import path
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
    path('category_brand_only/<str:brand>', views.category_brand_only, name='category_brand_only'), 
    # path('cart/', views.cart, name='cart'),
    path('login/', views.login_user, name="login"),
    path('logout/', views.logout_user, name="logout_user"),
    path('register/', views.register, name='register'),
    path("account/", views.account, name="account"),
    path('wishlist_view/', views.wishlist_view, name='wishlist_view'),
    path('add_to_wishlist/<int:product_id>/', views.add_to_wishlist, name='add_to_wishlist'),
    path('remove_from_wishlist/<int:product_id>/', views.remove_from_wishlist, name='remove_from_wishlist'),
    # path('add-to-cart/<int:product_id>/', )
    path('payment_page/', views.payment_page, name='payment_page'),
    path('payment/', views.payment, name='payment')
    

] 

