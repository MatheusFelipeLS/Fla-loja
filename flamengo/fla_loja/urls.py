from django.contrib import admin
from django.urls import path, include

from . import views

app_name = "fla_loja"

urlpatterns = [
  path('teste/', views.index, name='teste'),
  # path('product/', views.product, name='product'),
  path('product/<str:nick>', views.get_product_by_name, name='product'),
  path('data/', views.product_manager)
]