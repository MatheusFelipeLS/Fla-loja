from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.template import loader

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .models import *
from .serializer import *

import json




# +++++++++++++++++++++++++++++++++++++  Clients  +++++++++++++++++++++++++++++++++++++
@api_view(['GET'])
def clients(request):
    all_clients = Client.objects.all()
    template = loader.get_template("fla_loja/clients.html")
    context = {
        "clients": all_clients,
    }
    return HttpResponse(template.render(context, request))

def client_detail(request, id):
    client = get_object_or_404(Client, id=id)
    return render(request, 'fla_loja/client_detail.html', {'client': client})


# @api_view(['GET'])
# def clients(request):
#     # Supondo que você tenha um modelo Client para armazenar os dados dos clientes
#     clients = Client.objects.all()  # Puxa todos os clientes do banco de dados
#     return render(request, 'fla_loja/clients.html', {'clients': clients})

@api_view(['GET'])
def all_clients(request):
    all_clients = Client.objects.all()
    clients_data = [{'name': client.name, 'email': client.email} for client in all_clients]
    template = loader.get_template("fla_loja/all_clients.html")
    
    context = {
        "clients": clients_data,
    }
    
    return HttpResponse(template.render(context, request))


@api_view(['GET'])
def get_client(request, _index):
    try:
        client = Client.objects.get(pk=_index)
    except:
        return HttpResponse("Cliente não encontrado.", status=404)
    
    client_data = {
        'name': client.name,
        'email': client.email,
        'address': client.address,
        'cpf': client.cpf,
        'phone': client.phone
    }
    
    template = loader.get_template("fla_loja/all_clients/client.html")
    
    context = {
        "client": client_data,
    }
    
    return HttpResponse(template.render(context, request))


@api_view(['GET', 'PUT'])
def edit_client(request, _index):
    try:
        client = Client.objects.get(pk=_index)
    except:
        return HttpResponse("Cliente não encontrado.", status=404)
    
    if request.method == 'PUT':
        data = json.loads(request.body)
        client.name = data.get('name', client.name)
        client.email = data.get('email', client.email)
        client.address = data.get('address', client.address)
        client.cpf = data.get('cpf', client.cpf)
        client.phone = data.get('phone', client.phone)
        client.save()
        
        return JsonResponse({'message': 'Cliente atualizado com sucesso!'})


@api_view(['GET', 'POST'])
def add_client(request):
    if request.method == 'POST':

        name = request.POST.get('name')
        email = request.POST.get('email')
        address = request.POST.get('address')
        cpf = request.POST.get('cpf')
        phone = request.POST.get('phone')

        if name and email and cpf:
            if Client.objects.filter(cpf=cpf).exists():
                return HttpResponse("Erro: Um cliente com esse CPF já existe.", status=400)
            
            if Client.objects.filter(email=email).exists():
                return HttpResponse("Erro: Um cliente com esse email já existe.", status=400)
            
            Client.objects.create(name=name, email=email, address=address, cpf=cpf, phone=phone)
            return redirect('/fla_loja/all_clients')

    return render(request, 'fla_loja/all_clients/add_client.html')


@api_view(['GET', 'DELETE'])
def delete_client(request, _index):
    try:
        client = Client.objects.get(pk=_index)
    except:
        return HttpResponse("Cliente não encontrado.", status=404)
    
    client.delete()
    return redirect('/fla_loja/all_clients')




# +++++++++++++++++++++++++++++++++++++  Employees  +++++++++++++++++++++++++++++++++++++
@api_view(['GET'])
def all_employees(request):
    all_employees = Employee.objects.all()
    # employees_data = [{'name': employee.name, 'wage': employee.sales_count} for employee in all_employees]
    serializer = EmployeeSerializer(all_employees, many=True)
    # template = loader.get_template("fla_loja/all_employees.html")
    
    # context = {
    #     "employees": employees_data,
    # }
    
    return Response(serializer.data)
    
    # return HttpResponse(template.render(context, request))


@api_view(['GET'])
def get_employee(request, _index):
    try:
        employee = Employee.objects.get(pk=_index)
    except:
        return HttpResponse("Funcionário não encontrado.", status=404)
    
    employee_data = {
        'name': employee.name,
        'wage': employee.wage,
        'sales_count': employee.sales_count,
        'photo': employee.photo
    }
    
    template = loader.get_template("fla_loja/all_employees/employee.html")
    
    context = {
        "employee": employee_data,
    }
    
    return HttpResponse(template.render(context, request))


@api_view(['GET', 'PUT'])
def edit_employee(request, _index):
    try:
        employee = Employee.objects.get(pk=_index)
    except:
        return HttpResponse("Funcionário não encontrado.", status=404)
    
    if request.method == 'PUT':
        data = json.loads(request.body)
        employee.name = data.get('name', employee.name)
        employee.wage = data.get('wage', employee.wage)
        employee.sales_count = data.get('sales_count', employee.sales_count)
        employee.photo = data.get('photo', employee.photo)
        employee.save()
        
        return JsonResponse({'message': 'Funcionário atualizado com sucesso!'})


@api_view(['GET', 'POST'])
def add_employee(request):
    if request.method == 'POST':

        name = request.POST.get('name')
        wage = request.POST.get('wage')
        sales_count = request.POST.get('sales_count')
        photo = request.POST.get('photo')

        if name and wage:
            Employee.objects.create(name=name, wage=wage, sales_count=sales_count, photo=photo)
            return redirect('/fla_loja/all_employees')

    return render(request, 'fla_loja/all_employees/add_employee.html')


@api_view(['GET', 'DELETE'])
def delete_employee(request, _index):
    try:
        employee = Employee.objects.get(pk=_index)
    except:
        return HttpResponse("Funcionário não encontrado.", status=404)
    
    employee.delete()
    return redirect('/fla_loja/all_employees')


# +++++++++++++++++++++++++++++++++++++  Products  +++++++++++++++++++++++++++++++++++++
@api_view(['GET'])
def index(request):
    all_products = Product.objects.all()
    template = loader.get_template("fla_loja/index.html")
    context = {
        "all_products": all_products,
    }
    return HttpResponse(template.render(context, request))


# @api_view(['GET'])
# def index(request):
  
#   if request.method == 'GET':
#     products = Product.objects.all()
    
#     serializer = ProductSerializer(products, many=True)
#     return Response(serializer.data)
  
#   return Response(status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT'])
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
  
  
  # if request.method == 'PUT':
  #   serializer = ProductSerializer(product, data=request.data)
    
  #   if serializer.is_valid():
  #     serializer.save() 
  #     return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
    
  #   return Response(status=status.HTTP_400_BAD_REQUEST)
  


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


# @api_view(['GET'])
# def get_products(request):
  
#   if request.method == 'GET':
#     products = Product.objects.all()
    
#     serializer = ProductSerializer(products, many=True)
#     return Response(serializer.data)
  
#   return Response(status=status.HTTP_400_BAD_REQUEST)