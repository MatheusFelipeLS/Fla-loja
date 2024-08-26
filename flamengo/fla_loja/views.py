from django.shortcuts import render, redirect, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect, HttpResponseBadRequest
from django.template import loader
from django.urls import reverse
from django.contrib import messages
from django.utils.dateparse import parse_datetime

from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .models import *
from .serializer import *
from .forms import *

import shutil


# +++++++++++++++++++++++++++++++++++++  Clients  +++++++++++++++++++++++++++++++++++++
@api_view(['GET'])
def clients(request):
    all_clients = Client.objects.all()
    # template = loader.get_template("fla_loja/clients.html")
    template = loader.get_template("fla_loja/clients_copy.html")
    context = {
        "clients": all_clients,
    }
    return HttpResponse(template.render(context, request))


def client_detail(request, id):
    client = get_object_or_404(Client, id=id)
    return render(request, 'fla_loja/client_detail.html', {'client': client})


def edit_client(request, id):
    client = get_object_or_404(Client, id=id)
    
    if request.method == 'POST':
        form = ClientForm(request.POST, instance=client)
        if form.is_valid():
            form.save()
            return redirect('fla_loja:client_detail', id=client.id)
    else:
        form = ClientForm(instance=client)
    
    return render(request, 'fla_loja/edit_client.html', {'form': form, 'client': client})


def delete_client(request, id):
    client = get_object_or_404(Client, id=id)
    
    if request.method == 'POST':
        client.delete()
        return redirect('fla_loja:clients')
    
    return render(request, 'fla_loja/confirm_delete_client.html', {'client': client})


@api_view(['GET', 'POST'])
def add_client(request):
  
  if request.method == 'GET':
    
    template = loader.get_template("fla_loja/add_client_copy.html")
    context = {"a": 1,}
    return HttpResponse(template.render(context, request))
  
  if request.method == 'POST':
    new_client = request.data.copy()
    
    # Remova o csrfmiddlewaretoken
    if 'csrfmiddlewaretoken' in new_client:
        del new_client['csrfmiddlewaretoken']
    
    serializer = ClientSerializer(data=new_client)
    
    if(serializer.is_valid()):
      serializer.save()
      
      return redirect(request.path)
    
    print(serializer.errors)
    return Response(status=status.HTTP_400_BAD_REQUEST) 


# +++++++++++++++++++++++++++++++++++++  Employees  +++++++++++++++++++++++++++++++++++++

@api_view(['GET'])
def employees(request):
    all_employees = Employee.objects.all()
    # template = loader.get_template("fla_loja/employees.html")
    template = loader.get_template("fla_loja/employees_copy.html")
    context = {
        "employees": all_employees,
    }
    return HttpResponse(template.render(context, request))


def employee_detail(request, id):
    employee = get_object_or_404(Employee, id=id)
    return render(request, 'fla_loja/employee_detail.html', {'employee': employee})


def edit_employee(request, id):
    employee = get_object_or_404(Employee, id=id)
    
    if request.method == 'POST':
        form = EmployeeForm(request.POST, instance=employee)
        if form.is_valid():
            form.save()
            return redirect('fla_loja:employee_detail', id=employee.id)
    else:
        form = EmployeeForm(instance=employee)
    
    return render(request, 'fla_loja/edit_employee.html', {'form': form, 'employee': employee})


def delete_employee(request, id):
    employee = get_object_or_404(Employee, id=id)
    
    if request.method == 'POST':
        employee.delete()
        return redirect('fla_loja:employees')
    
    return render(request, 'fla_loja/confirm_delete_employee.html', {'employee': employee})


@api_view(['GET', 'POST'])
def add_employee(request):
  
  if request.method == 'GET':
    
    template = loader.get_template("fla_loja/add_employee_copy.html")
    context = {"a": 1,}
    return HttpResponse(template.render(context, request))
  
  if request.method == 'POST':
    new_employee = request.data.copy()
    
    # Remova o csrfmiddlewaretoken
    if 'csrfmiddlewaretoken' in new_employee:
        del new_employee['csrfmiddlewaretoken']
    
    serializer = EmployeeSerializer(data=new_employee)
    
    if(serializer.is_valid()):
      serializer.save()
      
      return redirect(request.path)
    
    print(serializer.errors)
    return Response(status=status.HTTP_400_BAD_REQUEST) 

# +++++++++++++++++++++++++++++++++++++  Products  +++++++++++++++++++++++++++++++++++++
@api_view(['GET', 'POST'])
def index(request):
    all_products = Product.objects.all()
    template = loader.get_template("fla_loja/index.html")
    context = {
        "all_products": all_products,
    }
    return HttpResponse(template.render(context, request))


@api_view(['GET', 'POST', 'PUT'])
def get_product_by_name(request, _id):
  try:
    product = Product.objects.get(pk=_id)
  except:
    return Response(status=status.HTTP_404_NOT_FOUND)
  
  if request.method == 'GET':
    serializer = ProductSerializer(product)
    template = loader.get_template("fla_loja/product.html")
    context = {
        "product": serializer.data,
    }
    return HttpResponse(template.render(context, request))
  
  if request.method == 'POST':
    serializer = ProductSerializer(product, data=request.data)
    
    if serializer.is_valid():
      serializer.save() 
    template = loader.get_template("fla_loja/product.html")
    context = {
        "product": serializer.data,
    }
    return HttpResponse(template.render(context, request))
  
  if request.method == 'PUT':
    
    serializer = ProductSerializer(product, data=request.data)
    
    if serializer.is_valid():
      serializer.save() 
      return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
    
    return Response(status=status.HTTP_400_BAD_REQUEST)
  

@api_view(['GET', 'POST', 'PUT'])
def edit_product(request, _id):
  #editando dados
  try:
    product = Product.objects.get(pk=_id)
  except:
    return Response(status=status.HTTP_404_NOT_FOUND)
  
  if request.method == 'GET':
    serializer = ProductSerializer(product)
    template = loader.get_template("fla_loja/edit_product.html")
    context = {
        "product": serializer.data,
    }
    return HttpResponse(template.render(context, request))
  
  if request.method == 'POST':
    serializer = ProductSerializer(product, data=request.data)
    
    if serializer.is_valid():
      serializer.save() 
      redirect(reverse(request.path))
    
    return Response(status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'POST'])
def create_product(request):
  
  if request.method == 'GET':
    
    template = loader.get_template("fla_loja/create_product_copy.html")
    context = {"a": 1,}
    return HttpResponse(template.render(context, request))
  
  if request.method == 'POST':
    new_product = request.data.copy()
    
    # Remova o csrfmiddlewaretoken
    if 'csrfmiddlewaretoken' in new_product:
        del new_product['csrfmiddlewaretoken']
    
    serializer = ProductSerializer(data=new_product)
    
    if(serializer.is_valid()):
      serializer.save()
      
      return redirect(request.path)
    
    print(serializer.errors)
    return Response(status=status.HTTP_400_BAD_REQUEST) 
  
  
@api_view(['GET', 'POST', 'DELETE'])
def delete_product(request, _id):
  if request.method == 'GET':
    try:
      product_to_delete = Product.objects.get(pk=_id)
    except:
      return Response(status=status.HTTP_404_NOT_FOUND)
    
    product_to_delete.delete()
    
    all_products = Product.objects.all()
    template = loader.get_template("fla_loja/index.html")
    context = {
        "all_products": all_products,
    }
    
    return HttpResponseRedirect(template.render(context, request), status=status.HTTP_202_ACCEPTED)


@api_view(['GET', 'POST', 'PUT', 'DELETE'])
def product_manager(request):
  #obtendo dados
  if request.method == 'GET':
    try:
      if request.GET['product']:
        product_nickname = request.GET['product']
        
        try: 
          product = Product.objects.get(pk=product_nickname)
        except:
          return Response(status=status.HTTP_404_NOT_FOUND)      
        
        serializer = ProductSerializer(product)
        
        return Response(serializer.data)
      
      else:
        return Response(status=status.HTTP_400_BAD_REQUEST)
      
    except:
      return Response(status=status.HTTP_400_BAD_REQUEST)
    
    
  #criando dados
  if request.method == 'POST':
    new_product = request.data
    
    serializer = ProductSerializer(data=new_product)
    
    if(serializer.is_valid()):
      serializer.save()
      return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    return Response(status=status.HTTP_400_BAD_REQUEST) 
  
  
  #editando dados
  if request.method == 'PUT':
    product_nickname = request.data['product_nickname']
    
    try:
      updated_product = Product.objects.get(pk=product_nickname)
    except:
      return Response(status=status.HTTP_404_NOT_FOUND)
    
      
    serializer = ProductSerializer(updated_product, data=request.data)
    
    if(serializer.is_valid()):
      serializer.save()
      return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
    
    return Response(status=status.HTTP_400_BAD_REQUEST) 
  
  #deletando dados
  if request.method == 'DELETE':
    
    try:
      product_to_delete = Product.objects.get(pk=request.data["product_nickname"])
      product_to_delete.delete()
      return Response(status=status.HTTP_202_ACCEPTED)
    except:
      return Response(status=status.HTTP_400_BAD_REQUEST)


def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Produto adicionado com sucesso!')
            return redirect('/')
    else:
        form = ProductForm()

    return render(request, 'fla_loja/add_product.html', {'form': form})




# +++++++++++++++++++++++++++++++++++++  Shopping  +++++++++++++++++++++++++++++++++++++
# def shopping_cart(request):
#     shoppings = Shopping.objects.all()
    
#     cart_data = []
#     for shopping in shoppings:
#         client = shopping.id_client
#         total_products = Sale.objects.filter(id_shopping=shopping).aggregate(total=models.Sum('quantity'))['total'] or 0
#         total_value = shopping.total_value
#         cart_data.append({
#             'client_name': client.name,
#             'total_products': total_products,
#             'total_value': total_value,
#             'shopping_id': shopping.id
#         })

#     context = {
#         'cart_data': cart_data
#     }
    
#     return render(request, 'fla_loja/shopping_cart.html', context)


# def shopping_detail(request, id):
#     shopping = get_object_or_404(Shopping, id=id)
    
#     sales = Sale.objects.filter(id_shopping=shopping)

#     products_data = []
#     for sale in sales:
#         product = sale.id_product
#         employee = sale.id_employee
#         products_data.append({
#             'product_name': product.name,
#             'quantity': sale.quantity,
#             'employee_name': employee.name,
#             'date_purchased': sale.data,
#             'product_price': product.price,
#             'total_price': sale.quantity * product.price
#         })

#     context = {
#         'shopping': shopping,
#         'products_data': products_data,
#         'client': shopping.id_client,
#         'total_value': shopping.total_value
#     }
    
#     return render(request, 'fla_loja/shopping_detail.html', context)


# def add_to_cart(request, product_id):
#     if request.method == 'POST':
#         client_id = request.POST.get('client_id')
#         employee_id = request.POST.get('employee_id')
#         quantity = request.POST.get('quantity')
#         date_purchased_str = request.POST.get('date_purchased')

#         if not date_purchased_str:
#             return HttpResponseBadRequest("A data e hora são obrigatórios.")

#         # Converter a data do formato string para datetime
#         date_purchased = parse_datetime(date_purchased_str)
#         if date_purchased is None:
#             return HttpResponseBadRequest("Formato de data e hora inválido. Use o formato YYYY-MM-DDTHH:MM.")

#         # Obter cliente, funcionário e produto com tratamento de erro
#         client = get_object_or_404(Client, id=client_id)
#         employee = get_object_or_404(Employee, id=employee_id)
#         product = get_object_or_404(Product, id=product_id)

#         # Criar ou atualizar a compra
#         shopping = Shopping.objects.create(id_client=client)
#         Sale.objects.create(id_shopping=shopping, id_product=product, id_employee=employee, quantity=quantity, data=date_purchased)

#         # Redirecionar para a página principal após a adição
#         messages.success(request, 'Produto adicionado ao carrinho com sucesso!')
#         return redirect('/')

#     return render(request, 'fla_loja/add_to_cart.html', {'product_id': product_id})


#funcional
# @api_view(['GET', 'POST'])
# def create_product(request):
#   if request.method == 'POST':
#     form = ProductForm(request.POST, request.FILES)  # Adicione request.FILES para lidar com upload de arquivos
#     if form.is_valid():
#         image = form.cleaned_data.get('image')

#         # Verificar se a foto já existe
#         if image and Product.objects.filter(image=image).exists():
#             messages.error(request, 'Já existe um empregado com essa foto.')
#         else:
#             # Salvar o novo empregado
#             form.save()
#             messages.success(request, 'Empregado adicionado com sucesso!')
#             return redirect('fla_loja:index')

#   else:
#       form = ProductForm()
  
#   return render(request, 'fla_loja/add_product.html', {'form': form})

#funcional
# def add_employee(request):
#     if request.method == 'POST':
#         form = EmployeeForm(request.POST, request.FILES)  # Adicione request.FILES para lidar com upload de arquivos
#         if form.is_valid():
#             photo = form.cleaned_data.get('photo')

#             # Verificar se a foto já existe
#             if photo and Employee.objects.filter(photo=photo).exists():
#                 messages.error(request, 'Já existe um empregado com essa foto.')
#             else:
#                 # Salvar o novo empregado
#                 form.save()
#                 messages.success(request, 'Empregado adicionado com sucesso!')
#                 return redirect('fla_loja:employees')
    
#     else:
#         form = EmployeeForm()
    
#     return render(request, 'fla_loja/add_employee.html', {'form': form})


# @api_view(['GET', 'POST'])
# def index(request):
#     all_products = Product.objects.all()
#     template = loader.get_template("fla_loja/index.html")
#     context = {
#         "all_products": all_products,
#     }
#     return HttpResponse(template.render(context, request))

#funcional
# def add_client(request):
#     if request.method == 'POST':
#         form = ClientForm(request.POST, request.FILES)  # Adicione request.FILES
#         if form.is_valid():
#             email = form.cleaned_data.get('email')
#             cpf = form.cleaned_data.get('cpf')
            
#             # Verificar se o e-mail ou CPF já existe
#             if Client.objects.filter(email=email).exists():
#                 messages.error(request, 'Já existe um cliente com esse e-mail.')
#             elif Client.objects.filter(cpf=cpf).exists():
#                 messages.error(request, 'Já existe um cliente com esse CPF.')
#             else:
#                 # Salvar o novo cliente
#                 form.save()
#                 messages.success(request, 'Cliente adicionado com sucesso!')
#                 return redirect('fla_loja:clients')
    
#     else:
#         form = ClientForm()
    
    # return render(request, 'fla_loja/add_client.html', {'form': form})