from django.contrib import admin
from django.urls import path, include

from . import views

app_name = "fla_loja"

urlpatterns = [
  path('', views.index, name='home'),
  
  path('product/<str:nick>', views.get_product_by_name, name='product'),
  path('data/', views.product_manager),
  
  path('employee/', views.all_employees, name='employee')
]