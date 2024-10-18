from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.template import loader
from django.contrib.auth import logout
from django.contrib.auth.hashers import make_password, check_password
from django.contrib import messages
from django.utils.dateparse import parse_datetime
from django.db.models import Sum

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from datetime import datetime

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
      
      last_client = Client.objects.last()
      Car.objects.create(
            id_client=last_client,
            status='Carrinho atual',
            date=datetime.today().strftime('%Y-%m-%d')
        )
      
      return redirect('/signin/')
    
    print(serializer.errors)
    return Response(status=status.HTTP_400_BAD_REQUEST) 


def log_out(request):
    logout(request)
    return redirect('/')


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
    

# +++++++++++++++++++++++++++++++++++++  Car  +++++++++++++++++++++++++++++++++++++
def mycar(request):
    car = Car.objects.get(id_client=request.session.get('id'), status='Carrinho atual')
    purchasesNotCompleted = PurchasesNotCompleted.objects.all()
    
    mc = []
    total_price = 0
    for purchase in purchasesNotCompleted:
        if(purchase.id_car.id == car.id):
            product = Product.objects.get(pk=purchase.id_product.id)
            price_per_purchase = product.price * purchase.quantity
            total_price += price_per_purchase
            mc.append(
                {
                    'id': purchase.id_product.id,
                    'image': product.image.url if product.image else None,
                    'name': product.name,
                    'quantity': purchase.quantity,
                    'price_per_purchase': price_per_purchase,
                }
            )
    
    context = {
        'isLogged': request.session.get('isLogged', False),
        'isEmployee': request.session.get('isEmployee', False),
        'car': mc,
        'total_price': total_price
    }
    
    return render(request, 'fla_loja/mycar.html', context)


def myorders(request):
    cars = Car.objects.filter(id_client=request.session.get('id'))
    purchasesCompleted = PurchasesCompleted.objects.all()
    
    purshased_products = []
    for purchase in purchasesCompleted:
        for car in cars:
            if(purchase.id_car.id == car.id):
                product = Product.objects.get(pk=purchase.id_product.id)
                purshased_products.append(
                    {
                        'id': car.id,
                        'name': product.name,
                        'quantity': purchase.quantity,
                        'price': product.price,
                        'image': product.image.url if product.image else None,
                        'status': car.status
                    }
                )
    
    context = {
        'isLogged': request.session.get('isLogged', False),
        'isEmployee': request.session.get('isEmployee', False),
        'purshased_products': purshased_products,
    }
    
    return render(request, 'fla_loja/my_orders.html', context)


def addtocar(request, _product_id):
    if request.method == 'GET':
        product = Product.objects.get(pk=_product_id)
        return render(
            request, 
            "fla_loja/add_to_car.html",
            {
                'isLogged': request.session.get('isLogged', False),
                'isEmployee': request.session.get('isEmployee', False),
                'product': product
            }
        )
    
    
    if request.method == 'POST':
        car = Car.objects.get(id_client=request.session.get('id'), status='Carrinho atual')
        product = Product.objects.get(pk=_product_id)
        
        quantity = int(request.POST.get("quantity"))
        
        PurchasesNotCompleted.objects.create(
                id_car=car,
                id_product=product,
                quantity=quantity
            )

        return redirect('/')


def buycar(request):
    if request.method == 'GET':
        return render(
            request, 
            "fla_loja/buy_car.html",
            {
                'isLogged': request.session.get('isLogged', False),
                'isEmployee': request.session.get('isEmployee', False),
            }
        )
        
    if request.method == 'POST':
        car = Car.objects.get(id_client=request.session.get('id'), status='Carrinho atual')
        
        employee = Employee.objects.get(pk=request.POST['employee_id'])
        payment_method = request.POST['payment_method']
        
        purchasesNotCompleted = PurchasesNotCompleted.objects.all()
    
        errors = False
        for purchase in purchasesNotCompleted:
            if(purchase.id_car.id == car.id):
                product = Product.objects.get(pk=purchase.id_product.id)
                if(product.quantity_in_stock - purchase.quantity <= 0):
                    messages.error(request, "Quantidade solicitada excede o estoque disponível.")
                    errors = True 
                    break
        
        
        if errors:
            return redirect('fla_loja:mycar')
            
                
        total_price = 0
        for purchase in purchasesNotCompleted:
            if(purchase.id_car.id == car.id):
                product = Product.objects.get(pk=purchase.id_product.id)
                product.quantity_in_stock -= purchase.quantity
                product.save()
                PurchasesCompleted.objects.create(
                    id_car=car,
                    id_product=product,
                    quantity=purchase.quantity
                )
                
                price_per_purchase = product.price * purchase.quantity
                total_price += price_per_purchase
                
                purchase.delete()
                
                
        employee.sales_count += total_price
        employee.save()
        
        car.id_employee = employee
        car.payment_method = payment_method
        car.date = datetime.today().strftime('%Y-%m-%d')
        car.status = "Pagamento pendente"
        car.save()
        
        Car.objects.create(
            id_client=Client.objects.get(pk=request.session.get('id')),
            status='Carrinho atual',
            date=datetime.today().strftime('%Y-%m-%d')
        )

        return redirect('fla_loja:index')
    

def paycar(request, _id_car):
    car = Car.objects.get(pk=_id_car)
    
    car.status = 'Compra finalizada'
    car.save()
    
    return redirect('fla_loja:myorders')


# +++++++++++++++++++++++++++++++++++++  Employees  +++++++++++++++++++++++++++++++++++++
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


def my_sales(request):
    cars = Car.objects.filter(id_employee=request.session.get('id'))
    purchasesCompleted = PurchasesCompleted.objects.all()
    
    purshased_products = []
    total_sales = 0
    for purchase in purchasesCompleted:
        for car in cars:
            if(purchase.id_car.id == car.id and car.status != 'Pagamento pendente'):
                product = Product.objects.get(pk=purchase.id_product.id)
                total_sales += purchase.quantity * product.price
                purshased_products.append(
                    {
                        'id': car.id,
                        'name': product.name,
                        'quantity': purchase.quantity,
                        'price': product.price,
                        'image': product.image.url if product.image else None,
                        'status': car.status
                    }
                )
    
    context = {
        'isLogged': request.session.get('isLogged', False),
        'isEmployee': request.session.get('isEmployee', False),
        'purshased_products': purshased_products,
        'total_sales': total_sales
    }
    
    return render(request, 'fla_loja/my_orders.html', context)


# +++++++++++++++++++++++++++++++++++++  Sales  +++++++++++++++++++++++++++++++++++++
@api_view(['GET'])
def sales_true(request):
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


@api_view(['GET'])
def sales(request):
    grouped_pursharse = PurchasesCompleted.objects.values('id_product').annotate(total_quantity=Sum('quantity'))
    
    total_per_product = []
    for compra in grouped_pursharse:
        product = Product.objects.get(pk=compra['id_product'])
        total_per_product.append(compra['quantity'] * product.price)
        
    context = {
        'isLogged': request.session.get('isLogged', False),
        'isEmployee': request.session.get('isEmployee', False),
        'grouped_pursharse': grouped_pursharse,
        'total_per_product': total_per_product 
    }
    
    return render(request, 'fla_loja/sales.html', context)


@api_view(['GET', 'POST'])
def individual_sale(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.method == "POST":
        client_id = request.session.get('id')
        employee_id = request.POST.get("employee_id")
        quantity = int(request.POST.get("quantity"))
        payment_method = request.POST.get("payment_method")
        date_purchased = datetime.today().strftime('%Y-%m-%d')
        status = 'Pagamento pendente'

        client = Client.objects.get(pk=client_id)
        employee = Employee.objects.get(pk=employee_id)
        
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
        
        
        Car.objects.create(
            id_client=client,
            id_employee=employee,
            date=parsed_date,
            status=status,
            payment_method=payment_method
        )
        
        last_car = Car.objects.last()

        PurchasesCompleted.objects.create(
            id_car=last_car,
            id_product=product,
            quantity=quantity
        )

        product.quantity_in_stock -= quantity
        product.save()

        employee.sales_count += (quantity * product.price)
        employee.save()

        return redirect('fla_loja:index')
    
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
        'isLogged': request.session.get('isLogged', False),
        'isEmployee': request.session.get('isEmployee', False),
        'stock_data': stock_data
    }
    
    return render(request, 'fla_loja/stock.html', context)
