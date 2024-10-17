from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

app_name = "fla_loja"

urlpatterns = [
    path('', views.index, name='index'),
    path('signin/', views.sign_in, name='sign_in'),
    path('signup/', views.sign_up, name='sign_up'),
    path('logout/', views.log_out, name='logout'),

    # +++++++++++++++++++++++++++  Produtos  +++++++++++++++++++++++++++
    path('product/<str:_id>', views.product_detail, name='product'),
    path('products/', views.filter_products, name='filter_products'),
    path('product/edit/<str:_id>', views.edit_product, name='edit_product'),
    path('product/create/', views.create_product, name='create_product'),
    path('product/delete/<str:_id>', views.delete_product, name='delete_product'),


    # +++++++++++++++++++++++++++  Clientes  +++++++++++++++++++++++++++
    path('clients/', views.clients, name='clients'),
    path('client/<int:id>/', views.client_detail, name='client_detail'),
    path('client/', views.client_detail_autoview, name='client_detail_autoview'),
    path('client/<int:id>/edit/', views.edit_client, name='edit_client'),
    path('client/<int:id>/delete/', views.delete_client, name='delete_client'),
    path('create_client/', views.create_client, name='create_client'),


    # +++++++++++++++++++++++++++  Vendedores  +++++++++++++++++++++++++++
    path('employees/', views.employees, name='employees'),
    path('employee/<int:id>/', views.employee_detail, name='employee_detail'),
    path('employee/', views.employee_detail_autoview, name='employee_detail_autoview'),
    path('employee/<int:id>/edit/', views.edit_employee, name='edit_employee'),
    path('employee/<int:id>/delete/', views.delete_employee, name='delete_employee'),
    path('create_employee/', views.create_employee, name='create_employee'),


    # +++++++++++++++++++++++++++  Vendas  +++++++++++++++++++++++++++
    path('sales/', views.sales, name='sales'),
    path('sale/<int:product_id>/', views.sale, name='sale'),
    path('delete_sale/<int:_id>/', views.delete_sale, name='delete_sale'),
    path('edit_sale/<int:_id>/', views.edit_sale, name='edit_sale'),


    # +++++++++++++++++++++++++++  Estoque  +++++++++++++++++++++++++++
    path('stock/', views.stock, name='stock'),
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
