from django import forms
from .models import *

class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['name', 'address', 'cpf', 'phone', 'email', 'password']

class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ['name', 'wage', 'sales_count', 'photo']
        

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'quantity_in_stock', 'image']
        
        
class PurchasesCompletedForm(forms.ModelForm):
    class Meta:
        model = PurchasesCompleted
        fields = ['id_car', 'id_product', 'quantity']
        