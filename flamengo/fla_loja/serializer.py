from rest_framework import serializers
from .models import Client, Employee, Sale, Product


class ClientSerializer(serializers.ModelSerializer):
  class Meta:
    model = Client
    fields = '__all__'

    
class EmployeeSerializer(serializers.ModelSerializer):
  class Meta:
    model = Employee
    fields = '__all__'

  def validate_salary(self, value):
      if value < 0:
          raise serializers.ValidationError("O salário não pode ser negativo.")
      return value

  def validate_number_of_sales(self, value):
      if value < 0:
          raise serializers.ValidationError("A quantidade de vendas não pode ser negativa.")
      return value
    
    
class SaleSerializer(serializers.ModelSerializer):
  class Meta:
    model = Sale
    fields = '__all__'
    
    
class ProductSerializer(serializers.ModelSerializer):
  class Meta:
    model = Product
    fields = '__all__'
