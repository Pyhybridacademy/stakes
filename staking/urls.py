from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('stake/', views.stake_form, name='stake_form'),
    path('order-card/', views.order_card, name='order_card'),
    path('connect-wallet/', views.connect_wallet, name='connect_wallet'),
    path('deposit/', views.deposit, name='deposit'),
    path('withdrawal/', views.withdrawal, name='withdrawal'),
    path('transactions/', views.transactions, name='transactions'),
    path('swap/', views.swap, name='swap'),
    path('buy_crypto', views.buy_crypto, name='buy_crypto'),
]