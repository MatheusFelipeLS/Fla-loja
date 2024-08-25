from django.contrib import admin
from django.urls import path, include

from . import views

app_name = "fla_loja"

urlpatterns = [
  path('', views.index, name='index'),
  
  path('product/<str:_id>', views.get_product_by_name, name='product'),
  path('product/edit/<str:_id>', views.edit_product, name='edit_product'),
  path('product/create/', views.create_product, name='create_product'),
  path('product/delete/<str:_id>', views.delete_product, name='delete_product'),
]