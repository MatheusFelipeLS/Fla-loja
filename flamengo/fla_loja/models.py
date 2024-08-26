from django.db import models

class Client(models.Model):
  name = models.CharField(max_length=100, default='')
  address = models.CharField(max_length=150, default='')
  cpf = models.CharField(max_length=14, default='')
  phone = models.CharField(max_length=15, default='')
  email = models.EmailField(default='')
  photo = models.ImageField(default='',upload_to=None, height_field=None, width_field=None, max_length=100)
  
  
class Employee(models.Model):
  name = models.CharField(max_length=100, default='')
  wage = models.FloatField(default=0.0)
  sales_count = models.IntegerField(default=0)
  photo = models.ImageField(default='', upload_to='flamengo/fla_loja/static/fla_loja/employee', height_field=None, width_field=None, max_length=100)

  
class Product(models.Model):
  name = models.CharField(max_length=50, default='')
  description = models.CharField(max_length=255, default='')
  price = models.FloatField(default=0.0)
  quantity_in_stock = models.IntegerField(default=0)
  image = models.ImageField(default='', upload_to='flamengo/fla_loja/static/fla_loja/products', height_field=None, width_field=None, max_length=100)
  
  
class Shopping(models.Model):
  id_client = models.ForeignKey(Client, on_delete=models.CASCADE)
  total_value = models.FloatField(default=0.0)
  

class Sale(models.Model):
  id_shopping = models.ForeignKey(Shopping, on_delete=models.CASCADE)
  id_product = models.ForeignKey(Product, on_delete=models.CASCADE)
  id_employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
  data = models.DateField("Date purchased")
  quantity = models.IntegerField(default=0)
