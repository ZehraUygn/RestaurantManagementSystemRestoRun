'api/urls.py'
"""project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from django.http import HttpResponse
from . import views
from django.shortcuts import redirect

app_name = 'api'

urlpatterns = [
    path('', lambda request: redirect('api:login'), name='root'),
    path('login/', views.loginPage, name='login'),
    path('logout/', views.logout, name='logout'),
    path('create/', views.create, name='create'),
    path('listeM/', views.listeM, name='listeM'),
    path('edit/<int:id>/', views.edit, name='edit'),
    path('update/<int:id>/', views.update, name='update'),
    path('delete/<int:id>/', views.delete, name='delete'),
    path('create_order/', views.createOrder, name='create_order'),
    path('stock/', views.manage_stock, name='manage_stock'),
    path('add-stock/<int:ingredient_id>/', views.add_stock, name='add_stock'),
    path('remove-stock/<int:ingredient_id>/', views.remove_stock, name='remove_stock'),
    path('stock-quantities/', views.stock_quantities, name='stock_quantities'),
    path('stock/<int:ingredient_id>/', views.stock_detail, name='stock_detail'),
    path('categories/', views.category_list, name='category_list'),
    path('category/add/', views.add_category, name='add_category'),
    path('category/edit/<int:category_id>/', views.edit_category, name='edit_category'),
    path('category/delete/<int:category_id>/', views.delete_category, name='delete_category'),
    path('add_ingredient/', views.add_or_update_ingredient, name='add_ingredient'),
    path('delete_ingredient/<int:ingredient_id>/', views.delete_ingredient, name='delete_ingredient'),
    path('tables/', views.table_list, name='table_list'),
    path('tables/<int:table_id>/', views.table_detail, name='table_detail'),
    path('orders/<int:order_id>/update/', views.update_order_status, name='update_order_status'),
    path('tables/update_status/<int:table_id>/', views.update_table_status, name='update_table_status'),
    path('set-stock/<int:ingredient_id>/', views.set_stock, name='set_stock'),
    path('manage_survey/', views.manage_survey, name='manage_survey'),
    path('survey/', views.survey, name='survey'),
    path('survey_thank_you/', views.survey_thank_you, name='survey_thank_you'),
    path('survey/delete/<int:question_id>/', views.delete_survey_question, name='delete_survey_question'),
    path('view_responses/', views.view_responses, name='view_responses'),
    path('orders/', views.view_orders, name='view_orders'),
]
