'cart/urls.py'
from django.urls import path
from . import views

urlpatterns = [
    path('', views.cartsum, name = "cartsum"),
    path('add/', views.cartadd, name="cartadd"),
    path('remove_item/<int:item_id>/', views.remove_item_from_order, name='remove_item_from_order'),
    path('checkout/', views.checkout, name='checkout'),
    path('submit-order/', views.submit_order, name='submit_order'),
    path('checkout/', views.checkout, name='checkout'),

]