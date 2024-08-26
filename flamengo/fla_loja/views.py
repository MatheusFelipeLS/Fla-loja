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




# +++++++++++++++++++++++++++++++++++++  Sales  +++++++++++++++++++++++++++++++++++++
def sales(request):
    # Obter todas as vendas
    sales = Sale.objects.select_related('id_client', 'id_product', 'id_employee').all()
    
    # Preparar os dados para a tabela
    sales_data = []
    for sale in sales:
        sales_data.append({
            'id': sale.id,  # Inclua o ID da venda aqui
            'client_name': sale.id_client.name,
            'product_name': sale.id_product.name,
            'quantity': sale.quantity,
            'total_price': sale.quantity * sale.id_product.price,
            'employee_name': sale.id_employee.name,  # Nome do vendedor
            'date': sale.data.strftime('%Y-%m-%d')  # Data da compra no formato YYYY-MM-DD
        })
    
    context = {
        'sales_data': sales_data
    }
    
    return render(request, 'fla_loja/sales.html', context)


def sale(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.method == "POST":
        client_id = request.POST.get("client_id")
        employee_id = request.POST.get("employee_id")
        date_purchased = request.POST.get("date_purchased")
        quantity = int(request.POST.get("quantity"))

        # Validate the client and employee IDs
        client = Client.objects.filter(id=client_id).first()
        employee = Employee.objects.filter(id=employee_id).first()
        
        if not client or not employee:
            messages.error(request, "Cliente ou Vendedor inválido.")
            return render(request, 'fla_loja/sale.html', {'product': product})
        
        # Check if quantity is available in stock
        if quantity > product.quantity_in_stock:
            messages.error(request, "Quantidade solicitada excede o estoque disponível.")
            return render(request, 'fla_loja/sale.html', {'product': product})
        
        try:
            # Parse the date
            parsed_date = parse_datetime(date_purchased)
            if parsed_date is None:
                raise ValueError("Data inválida")
        except ValueError as e:
            messages.error(request, f"Erro na data: {e}")
            return render(request, 'fla_loja/sale.html', {'product': product})
        
        # Create the sale
        Sale.objects.create(
            id_client=client,
            id_product=product,
            id_employee=employee,
            data=parsed_date,
            quantity=quantity
        )

        # Update the product's stock
        product.quantity_in_stock -= quantity
        product.save()

        return redirect('fla_loja:sales')
    
    return render(request, 'fla_loja/sale.html', {'product': product})


def sale_detail(request, sale_id):
    # Obter a venda com o ID fornecido
    sale = get_object_or_404(Sale, id=sale_id)
    
    # Preparar os dados para o contexto
    context = {
        'client_name': sale.id_client.name,
        'employee_name': sale.id_employee.name,
        'product_image': sale.id_product.image.url,  # Assegure-se de que o caminho da imagem está correto
        'product_name': sale.id_product.name,
        'product_description': sale.id_product.description,
        'quantity': sale.quantity,
        'total_price': sale.quantity * sale.id_product.price,
    }
    
    return render(request, 'fla_loja/sale_detail.html', context)


def delete_sale(request, sale_id):
    if request.method == "POST":
        sale = get_object_or_404(Sale, id=sale_id)
        sale.delete()
        # Redirecionar de volta para a página de vendas após a exclusão
        return redirect('sales')
    # Opcional: Pode retornar um erro se a requisição não for POST
    return redirect('sales')




# +++++++++++++++++++++++++++++++++++++  Estoque  +++++++++++++++++++++++++++++++++++++
# views.py
from django.shortcuts import render
from .models import Product

def stock(request):
    # Obter todos os produtos
    products = Product.objects.all()
    
    # Preparar os dados para a tabela
    stock_data = []
    for product in products:
        total_price = product.price * product.quantity_in_stock
        stock_data.append({
            'id': product.id,  # Inclua o ID do produto aqui
            'image': product.image.url if product.image else None,
            'name': product.name,
            'quantity': product.quantity_in_stock,
            'total_price': total_price,
        })
    
    context = {
        'stock_data': stock_data
    }
    
    return render(request, 'fla_loja/stock.html', context)
