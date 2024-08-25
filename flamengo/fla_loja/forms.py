from django import forms
from .models import *

class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['name', 'address', 'cpf', 'phone', 'email', 'photo']

class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ['name', 'wage', 'sales_count', 'photo']