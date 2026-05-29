from django.urls import path
from . import views

urlpatterns = [
    # 🏠 Home
    path('', views.home, name='home'),

    # 📂 Category & Products
    path('category/<int:category_id>/',
         views.category_products, name='category_products'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),

    # 🛒 Cart
    path('add-to-cart/<int:product_id>/',
         views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart, name='cart'),
    path('checkout/', views.checkout, name='checkout'),

    # 💳 Payment Simulation
    path('payment/<str:order_id>/', views.payment_page, name='payment_page'),

    # 📦 Orders
    path('order-success/<str:order_id>/',
         views.order_success, name='order_success'),
    path('orders/', views.order_history, name='order_history'),
    path('order/<str:order_id>/', views.order_detail, name='order_detail'),

    # 📄 Download Invoice (PDF)
    path('download-invoice/<str:order_id>/',
         views.download_invoice, name='download_invoice'),

    # ❌ Cancel Order (POST only)
    path('cancel-order/<str:order_id>/',
         views.cancel_order, name='cancel_order'),

    # 🔐 Authentication
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
]
