from django.urls import path
from . import views

app_name = "fla_loja"

urlpatterns = [
    path('', views.index, name='home'),
    path('product/<str:_id>', views.get_product_by_name, name='product'),
    path('data/', views.product_manager),
    path('clients/', views.clients, name='clients'),
    path('client/<int:id>/', views.client_detail, name='client_detail'),  # Certifique-se de que esta linha está presente
]
