from django.urls import path
from . import views

app_name = "fla_loja"

urlpatterns = [
    path('', views.index, name='home'),
    path('product/<str:_id>', views.get_product_by_name, name='product'),
    path('data/', views.product_manager),

    # +++++++++++++++++++++++++++  Clientes  +++++++++++++++++++++++++++
    path('clients/', views.clients, name='clients'),
    path('client/<int:id>/', views.client_detail, name='client_detail'),
    path('client/<int:id>/edit/', views.edit_client, name='edit_client'),
    path('client/<int:id>/delete/', views.delete_client, name='delete_client'),
    path('add_client/', views.add_client, name='add_client'),


    # +++++++++++++++++++++++++++  Vendedores  +++++++++++++++++++++++++++
    path('employees/', views.employees, name='employees'),
    path('employee/<int:id>/', views.employee_detail, name='employee_detail'),
    path('employee/<int:id>/edit/', views.edit_employee, name='edit_employee'),
    path('employee/<int:id>/delete/', views.delete_employee, name='delete_employee'),
    path('add_employee/', views.add_employee, name='add_employee'),
]
