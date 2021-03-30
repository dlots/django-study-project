from django.urls import path
from . import views

urlpatterns = [
    path('', views.render_catalog, name='shop_catalog'),
    path('<int:product_id>', views.product, name='product_by_id'),
    path('login', views.log_in, name='shop_login'),
    path('logout', views.log_out, name='shop_logout'),
    path('signup', views.sign_up, name='shop_signup'),
    path('cart', views.request_cart, name='cart'),
    path('checkout', views.checkout, name='checkout')
]