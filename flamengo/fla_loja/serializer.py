from rest_framework import serializers

from .models import Client, Employee, Sale, Shopping, Product


class ClientSerializer(serializers.ModelSerializer):
  class Meta:
    model = Client
    fields = '__all__'

    
class EmployeeSerializer(serializers.ModelSerializer):
  class Meta:
    model = Employee
    fields = '__all__'
    
    
class SaleSerializer(serializers.ModelSerializer):
  class Meta:
    model = Sale
    fields = '__all__'
    
    
class ShoppingSerializer(serializers.ModelSerializer):
  class Meta:
    model = Shopping
    fields = '__all__'
    
    
class ProductSerializer(serializers.ModelSerializer):
  class Meta:
    model = Product
    fields = '__all__'
