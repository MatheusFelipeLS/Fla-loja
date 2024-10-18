from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

from django.contrib import admin

app_name = "fla_loja"

urlpatterns = [
    path('admin/', admin.site.urls),
    
    
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


    # +++++++++++++++++++++++++++  Car  +++++++++++++++++++++++++++
    path('car/', views.mycar, name='mycar'),
    path('myorders/', views.myorders, name='myorders'),
    path('addtocar/<int:_product_id>/', views.addtocar, name='addtocar'),
    path('buycar/', views.buycar, name='buycar'),
    path('paycar/<int:_id_car>', views.paycar, name='paycar'),

    # +++++++++++++++++++++++++++  Vendedores  +++++++++++++++++++++++++++
    path('employee/', views.employee_detail_autoview, name='employee_detail_autoview'),
    path('my_sales/', views.my_sales, name='my_sales'),

    # +++++++++++++++++++++++++++  Vendas  +++++++++++++++++++++++++++
    path('sales/', views.sales, name='sales'),
    path('sale/<int:product_id>/', views.individual_sale, name='individual_sale'),
    path('delete_sale/<int:_id>/', views.delete_sale, name='delete_sale'),
    path('edit_sale/<int:_id>/', views.edit_sale, name='edit_sale'),

    # +++++++++++++++++++++++++++  Estoque  +++++++++++++++++++++++++++
    path('stock/', views.stock, name='stock'),
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
