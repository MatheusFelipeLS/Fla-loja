from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.template import loader
from django.contrib.auth import logout
from django.contrib.auth.hashers import make_password, check_password
from django.contrib import messages
from django.utils.dateparse import parse_datetime

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .models import *
from .serializer import *
from .forms import *

@api_view(['GET', 'POST'])
def index(request):
    all_products = Product.objects.all()
    return render(
        request, 
        "fla_loja/index.html", 
        {
            'isLogged': request.session.get('isLogged', False),
            'isEmployee': request.session.get('isEmployee', False),
            'all_products': all_products
        }
    )


def sign_in(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        
        try:
            client = Client.objects.get(email=email)
            
            # Verificar se a senha está correta
            if check_password(password, client.password):
                request.session['id'] = client.id
                request.session['isLogged'] = True
                request.session['isEmployee'] = False
                return redirect('/')  
            else:
                messages.error(request, 'Senha incorreta.')
        except Client.DoesNotExist:
            try:
                employee = Employee.objects.get(email=email)
                if password == employee.password:
                    request.session['id'] = employee.id
                    request.session['isLogged'] = True
                    request.session['isEmployee'] = True
                    return redirect('/') 
            except Employee.DoesNotExist:
                messages.error(request, 'Email e/ou senha incorreto(s)')
    
    return render(request, 'fla_loja/sign_in.html')


@api_view(['GET', 'POST'])
def sign_up(request):
  if request.method == 'GET':
    return render(request, "fla_loja/sign_up.html")
  
  if request.method == 'POST':
    new_client = request.data.copy()
    
    new_client['password'] = make_password(new_client['password'])
    
    # Remova o csrfmiddlewaretoken
    if 'csrfmiddlewaretoken' in new_client:
        del new_client['csrfmiddlewaretoken']
    
    serializer = ClientSerializer(data=new_client)
    
    if(serializer.is_valid()):
      serializer.save()
      
      return redirect('/signin/')
    
    print(serializer.errors)
    return Response(status=status.HTTP_400_BAD_REQUEST) 


def log_out(request):
    logout(request)
    return redirect('/')


# +++++++++++++++++++++++++++++++++++++  Clients  +++++++++++++++++++++++++++++++++++++
@api_view(['GET'])
def clients(request):
    all_clients = Client.objects.all()
    template = loader.get_template("fla_loja/clients.html")
    context = {
        'isLogged': request.session.get('isLogged', False),
        'isEmployee': request.session.get('isEmployee', False),
        "clients": all_clients,
    }
    return HttpResponse(template.render(context, request))


@api_view(['GET'])
def client_detail_autoview(request):
    client = Client.objects.get(id=request.session.get('id'))
    return render(
        request, 
        'fla_loja/client_detail.html', 
        {
            'isLogged': request.session.get('isLogged', False),
            'isEmployee': request.session.get('isEmployee', False),
            'client': client
        }
    )
    

@api_view(['GET'])
def client_detail(request, id):
    client = get_object_or_404(Client, id=id)
    return render(
        request, 
        'fla_loja/client_detail.html', 
        {
            'isLogged': request.session.get('isLogged', False),
            'isEmployee': request.session.get('isEmployee', False),
            'client': client
        }
    )


@api_view(['GET', 'POST'])
def edit_client_true(request, id):
    client = get_object_or_404(Client, id=id)
    
    if request.method == 'POST':
        form = ClientForm(request.POST, instance=client)
        if form.is_valid():
            form.save()
            return redirect('fla_loja:client_detail', id=client.id)
    else:
        form = ClientForm(instance=client)
    
    return render(
        request, 
        'fla_loja/edit_client.html', 
        {
            'isLogged': request.session.get('isLogged', False),
            'isEmployee': request.session.get('isEmployee', False),
            'form': form, 
            'client': client
        }
    )

@api_view(['GET', 'POST'])
def edit_client(request, id):
    try:
        client = Client.objects.get(pk=id)
    except Client.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        serializer = ClientSerializer(client)
        template = loader.get_template("fla_loja/edit_client.html")
        context = {
            'isLogged': request.session.get('isLogged', False),
            'isEmployee': request.session.get('isEmployee', False),
            "client": serializer.data,
        }
        return HttpResponse(template.render(context, request))

    if request.method == 'POST':
        data = request.data.copy()
        if data['password'] != '':
            data['password'] = make_password(data['password'])
            
        serializer = ClientSerializer(client, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            
            return redirect('/')
        
        return render(
            request, 
            "fla_loja/edit_client.html", 
            {
                'isLogged': request.session.get('isLogged', False),
                'isEmployee': request.session.get('isEmployee', False),
                "client": data
            }
        )


@api_view(['GET', 'POST'])
def delete_client(request, id):
    client = get_object_or_404(Client, id=id)
    
    if request.method == 'POST':
        client.delete()
        return redirect('fla_loja:clients')
    
    return render(
        request, 
        'fla_loja/confirm_delete.html', 
        {
            'type': 'Cliente',
            'client': client,
            'is_employee': 0,
        }
    )


@api_view(['GET', 'POST'])
def create_client(request):
  if request.method == 'GET':
    return render(
        request, 
        "fla_loja/create_client.html",
        {
            'isLogged': request.session.get('isLogged', False),
            'isEmployee': request.session.get('isEmployee', False),
        }
    )
  
  if request.method == 'POST':
    new_client = request.data.copy()
    
    new_client['password'] = make_password('')
    
    # Remova o csrfmiddlewaretoken
    if 'csrfmiddlewaretoken' in new_client:
        del new_client['csrfmiddlewaretoken']
    
    serializer = ClientSerializer(data=new_client)
    
    if(serializer.is_valid()):
      serializer.save()
      
      return redirect('/clients/')
    
    print(serializer.errors)
    return Response(status=status.HTTP_400_BAD_REQUEST) 


# +++++++++++++++++++++++++++++++++++++  Employees  +++++++++++++++++++++++++++++++++++++
@api_view(['GET'])
def employees(request):
    all_employees = Employee.objects.all()
    template = loader.get_template("fla_loja/employees.html")
    context = {
        "employees": all_employees,
    }
    return HttpResponse(template.render(context, request))


@api_view(['GET'])
def employee_detail_autoview(request):
    employee = Employee.objects.get(id=request.session.get('id'))
    return render(
        request, 
        'fla_loja/employee_detail.html', 
        {
            'isLogged': request.session.get('isLogged', False),
            'isEmployee': request.session.get('isEmployee', False),
            'employee': employee
        }
    )


@api_view(['GET'])
def employee_detail(request, id):
    employee = get_object_or_404(Employee, id=id)
    return render(request, 'fla_loja/employee_detail.html', {'employee': employee})


@api_view(['GET', 'POST'])
def edit_employee(request, id):
    employee = get_object_or_404(Employee, id=id)
    
    if request.method == 'POST':
        form = EmployeeForm(request.POST, instance=employee)

        if form.is_valid():
            # Verificação manual para salário e número de vendas
            salary = form.cleaned_data.get('wage', 0)
            number_of_sales = form.cleaned_data.get('sales_count', 0)

            errors = False
            if salary < 0:
                messages.error(request, "Salário não pode ser negativo.")
                errors = False

            if number_of_sales < 0:
                messages.error(request, "Quantidade de vendas não pode ser negativa.")
                errors = False

            if errors:
                return render(request, 'fla_loja/edit_employee.html', {'form': form, 'employee': employee})
            
            
            # Se tudo estiver correto, salvar as alterações
            form.save()
            return redirect('fla_loja:employee_detail', id=employee.id)
    else:
        form = EmployeeForm(instance=employee)
    
    return render(request, 'fla_loja/edit_employee.html', {'form': form, 'employee': employee})


@api_view(['GET', 'POST'])
def delete_employee(request, id):
    employee = get_object_or_404(Employee, id=id)
    
    if request.method == 'POST':
        employee.delete()
        return redirect('fla_loja:employees')
    
    return render(
        request, 
        'fla_loja/confirm_delete.html', 
        {
            'type': 'Vendedor',
            'employee': employee,
            'is_employee': 1
            
        }
    )


@api_view(['GET', 'POST'])
def create_employee(request):
    if request.method == 'GET':
        return render(request, "fla_loja/create_employee.html")

    if request.method == 'POST':
        new_employee = request.data.copy()

        # Remova o csrfmiddlewaretoken
        if 'csrfmiddlewaretoken' in new_employee:
            del new_employee['csrfmiddlewaretoken']

        # Verificação manual para salário e número de vendas
        salary = float(new_employee.get('wage', 0))
        number_of_sales = int(new_employee.get('sales_count', 0))

        errors = False
        if salary < 0:
            messages.error(request, "Salário não pode ser negativo.")
            errors = True

        if number_of_sales < 0:
            messages.error(request, "Quantidade de vendas não pode ser negativa.")
            errors = True

        # Verificação para fotos duplicadas
        photo = new_employee.get('photo')
        if Employee.objects.filter(photo=photo).exists():
            messages.error(request, "Já existe um funcionário com esta foto.")
            errors = True

        if errors:
            return render(request, "fla_loja/create_employee.html", {"form": EmployeeForm()})
        
        
        # Se tudo estiver correto, salvar o funcionário
        serializer = EmployeeSerializer(data=new_employee)
        if serializer.is_valid():
            serializer.save()
            return redirect('/employees/')

        print(serializer.errors)
        return Response(status=status.HTTP_400_BAD_REQUEST)


# +++++++++++++++++++++++++++++++++++++  Products  +++++++++++++++++++++++++++++++++++++
@api_view(['GET', 'POST'])
def product_detail(request, _id):
  try:
    product = Product.objects.get(pk=_id)
  except:
    return Response(status=status.HTTP_404_NOT_FOUND)
  
  if request.method == 'GET':
    serializer = ProductSerializer(product)
    template = loader.get_template("fla_loja/product_detail.html")
    context = {
        'isLogged': request.session.get('isLogged', False),
        'isEmployee': request.session.get('isEmployee', False),
        "product": serializer.data,
    }
    return HttpResponse(template.render(context, request))
  
  if request.method == 'POST':
    serializer = ProductSerializer(product, data=request.data)
    
    if serializer.is_valid():
      serializer.save() 
    template = loader.get_template("fla_loja/product_detail.html")
    context = {
        'isLogged': request.session.get('isLogged', False),
        'isEmployee': request.session.get('isEmployee', False),
        "product": serializer.data,
    }
    return HttpResponse(template.render(context, request))


@api_view(['GET', 'POST'])
def filter_products(request):
    if request.method == 'GET':
        return render(
            request, 
            "fla_loja/filter_products.html",
            {
                'isLogged': request.session.get('isLogged', False),
                'isEmployee': request.session.get('isEmployee', False),
            }
        )
    
    elif request.method == 'POST':
        products = Product.objects.all()
        
        if request.POST.get("checkbox_name") == '':
            name = request.POST.get("name")
            if name:
                products = products.filter(name__icontains=name)
                    
        if request.POST.get("checkbox_price") == '':
            low_price = request.POST.get("low_price")
            high_price = request.POST.get("high_price")
            if low_price:
                products = products.filter(price__gte=low_price)
            if high_price:
                products = products.filter(price__lte=high_price)
            
        if request.POST.get("checkbox_category") == '':
            category = request.POST.get("category")
            if category:
                products = products.filter(category__exact=category)
            
        if request.POST.get("checkbox_mari") == '':
            products = products.filter(made_in__exact='Mari')
            
        if request.POST.get("checkbox_less5") == '':
            products = products.filter(quantity_in_stock__lte=4)
        
        return render(
            request, 
            "fla_loja/filtered_products.html",
            {
                'isLogged': request.session.get('isLogged', False),
                'isEmployee': request.session.get('isEmployee', False),
                'all_products': products
            }
        )


@api_view(['GET', 'POST'])
def edit_product(request, _id):
    try:
        product = Product.objects.get(pk=_id)
    except Product.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        serializer = ProductSerializer(product)
        template = loader.get_template("fla_loja/edit_product.html")
        context = {
            'isLogged': request.session.get('isLogged', False),
            'isEmployee': request.session.get('isEmployee', False),
            "product": serializer.data,
        }
        return HttpResponse(template.render(context, request))

    if request.method == 'POST':
        data = request.data.copy()

        # Verificação manual para preço e quantidade em estoque
        try:
            price = float(data.get('price', 0))
            quantity_in_stock = int(data.get('quantity_in_stock', 0))

            errors = False
            if price < 0:
                messages.error(request, "O preço não pode ser negativo.")
                errors = True

            if quantity_in_stock < 0:
                messages.error(request, "A quantidade em estoque não pode ser negativa.")
                errors = True
            
            if errors:
                return render(request, "fla_loja/edit_product.html", {"product": data})

        except ValueError as e:
            messages.error(request, f"Erro nos dados fornecidos: {e}")
            return render(request, "fla_loja/edit_product.html", {"product": data})

        # Se tudo estiver correto, atualizar o produto
        serializer = ProductSerializer(product, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            # Redireciona para a página de detalhes do produto
            return redirect('fla_loja:product', _id=_id)
        
        return render(request, "fla_loja/edit_product.html", {"product": data})


@api_view(['GET', 'POST'])
def create_product(request):
    if request.method == 'GET':
        return render(
            request, 
            "fla_loja/create_product.html",
            {
                'isLogged': request.session.get('isLogged', False),
                'isEmployee': request.session.get('isEmployee', False),
            }
        )

    if request.method == 'POST':
        new_product = request.data.copy()

        # Remova o csrfmiddlewaretoken
        if 'csrfmiddlewaretoken' in new_product:
            del new_product['csrfmiddlewaretoken']

        # Verificação manual para preço e quantidade em estoque
        try:
            price = float(new_product.get('price', 0))
            quantity_in_stock = int(new_product.get('quantity_in_stock', 0))

            errors = False
            if price < 0:
                messages.error(request, "O preço não pode ser negativo.")
                errors = True

            if quantity_in_stock < 0:
                messages.error(request, "A quantidade em estoque não pode ser negativa.")
                errors = True

            if errors:
                return render(request, "fla_loja/create_product.html", {"form": new_product})
            
            
        except ValueError as e:
            messages.error(request, f"Erro nos dados fornecidos: {e}")
            return render(request, "fla_loja/create_product.html", {"form": new_product})

        # Se tudo estiver correto, salvar o produto
        serializer = ProductSerializer(data=new_product)
        if serializer.is_valid():
            serializer.save()
            return redirect('/')
        
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
    
    return redirect('/')


# +++++++++++++++++++++++++++++++++++++  Sales  +++++++++++++++++++++++++++++++++++++
@api_view(['GET'])
def sales(request):
    sales = Sale.objects.select_related('id_client', 'id_product', 'id_employee').all()
    
    # Preparar os dados para a tabela
    sales_data = []
    for sale in sales:
      client = "Indisp."
      employee = "Indisp."
      product = "Indisp."
      total_price = sale.quantity
      if sale.id_client:
        client = sale.id_client.name
      if sale.id_employee:
        employee = sale.id_employee.name
      if sale.id_product:
        total_price *= sale.id_product.price
        product = sale.id_product.name 
      else:
        total_price = ' Indisp.'
        
      sales_data.append({
          'id': sale.id,  # Inclua o ID da venda aqui
          'client_name': client,
          'product_name': product,
          'quantity': sale.quantity,
          'total_price': total_price,
          'employee_name': employee,  # Nome do vendedor
          'date': sale.data.strftime('%Y-%m-%d')  # Data da compra no formato YYYY-MM-DD
      })
    
    context = {
        'sales_data': sales_data
    }
    
    return render(request, 'fla_loja/sales.html', context)


@api_view(['GET', 'POST'])
def sale(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.method == "POST":
        client_id = request.POST.get("client_id")
        employee_id = request.POST.get("employee_id")
        date_purchased = request.POST.get("date_purchased")
        quantity = int(request.POST.get("quantity"))

        client = Client.objects.filter(id=client_id).first()
        employee = Employee.objects.filter(id=employee_id).first()
        
        errors = False
        if not client or not employee:
            messages.error(request, "Cliente ou Vendedor inválido.")
            errors = True
        
        
        if quantity > product.quantity_in_stock:
            messages.error(request, "Quantidade solicitada excede o estoque disponível.")
            errors = True
        
        
        if errors:
            return render(request, 'fla_loja/sale.html', {'product': product})    
        
        try:
            parsed_date = parse_datetime(date_purchased)
            if parsed_date is None:
                raise ValueError("Data inválida")
        except ValueError as e:
            messages.error(request, f"Erro na data: {e}")
            return render(request, 'fla_loja/sale.html', {'product': product})
        
        
        Sale.objects.create(
            id_client=client,
            id_product=product,
            id_employee=employee,
            data=parsed_date,
            quantity=quantity
        )

        product.quantity_in_stock -= quantity
        product.save()

        employee.sales_count += 1
        employee.save()

        return redirect('fla_loja:sales')
    
    return render(
        request, 
        'fla_loja/sale.html', 
        {
            'isLogged': request.session.get('isLogged', False),
            'isEmployee': request.session.get('isEmployee', False),
            'product': product
        }
    )
  

@api_view(['GET', 'POST', 'DELETE'])
def delete_sale(request, _id):
  if request.method == 'GET':
    try:
      sale_to_delete = Sale.objects.get(pk=_id)
    except:
      return Response(status=status.HTTP_404_NOT_FOUND)
    
    sale_to_delete.delete()
    
    return redirect('/sales/')


@api_view(['GET', 'POST'])
def edit_sale(request, _id):
    sale = get_object_or_404(Sale, id=_id)
    if sale.id_product:
      product = get_object_or_404(Product, id=sale.id_product.id)
    if sale.id_employee:
      employee = get_object_or_404(Employee, id=sale.id_employee.id)
    
    if request.method == 'POST':
        product.quantity_in_stock += sale.quantity
        employee.sales_count += sale.quantity
        form = SaleForm(request.POST, instance=sale)
        if form.is_valid():
            product.quantity_in_stock -= int(request.POST.get('quantity'))
            
            employee.sales_count -= int(request.POST.get('quantity'))
            
            prod_serializer = ProductSerializer(data=product)
            if prod_serializer.is_valid():
              prod_serializer.save()
              
            employee_serializer = EmployeeSerializer(data=employee)
            if employee_serializer.is_valid():
              employee_serializer.save()
            
            form.save()
            return redirect('/sales/')
        product.quantity_in_stock -= sale.quantity
        employee.sales_count -= sale.quantity
    else:
        form = SaleForm(instance=sale)
    
    return render(request, 'fla_loja/edit_sale.html', { 'form': form, 'sale': sale })

# +++++++++++++++++++++++++++++++++++++  Estoque  +++++++++++++++++++++++++++++++++++++
@api_view(['GET'])
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
