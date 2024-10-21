from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.template import loader
from django.contrib.auth import logout
from django.contrib.auth.hashers import make_password, check_password
from django.contrib import messages
from django.utils.dateparse import parse_datetime
from django.db.models import Count
from django.db import connection

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from datetime import datetime

from .models import *
from .serializer import *
from .forms import *

CUPONS = {
    "FLAMENGO": 0.10,
    "ONEPIECE": 0.10,
    "SOUSA": 0.10
}

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


def call_get_low_stock_products():
    with connection.cursor() as cursor:
        cursor.execute("CALL get_low_stock_products()")

        # Fetch todos os resultados
        products = cursor.fetchall()

    return products


def low_stock_view(request):
    low_stock_products = call_get_low_stock_products()
    return render(
        request, 
        'low_stock.html', 
                  {
                    'isLogged': request.session.get('isLogged', False),
                    'isEmployee': request.session.get('isEmployee', False),
                    'products': low_stock_products,
                }
            )


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
        
        if request.POST.get("checkbox_less5") == '':
            low_stock_products = call_get_low_stock_products()
            return render(
                request, 
                "fla_loja/filtered_products.html",
                {
                    'isLogged': request.session.get('isLogged', False),
                    'isEmployee': request.session.get('isEmployee', False),
                    'all_products': low_stock_products
                }
            )
            # products = products.filter(quantity_in_stock__lte=4)
        
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
    product = Product.objects.get(pk=_id)
    
    if not product:
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
        print("id: ", _id)

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
                return render(
                    request, 
                    "fla_loja/edit_product.html", 
                    {"product": data})

        except ValueError as e:
            messages.error(request, f"Erro nos dados fornecidos: {e}")
            return render(request, "fla_loja/edit_product.html", {"product": data})

        # Se tudo estiver correto, chamar a stored procedure para atualizar o produto
        try:
            with connection.cursor() as cursor:
                cursor.execute('CALL updt_product(%s, %s, %s, %s, %s, %s, %s)', [
                    _id,
                    data.get('name'),
                    price,
                    quantity_in_stock,
                    data.get('description'),
                    data.get('category'),
                    data.get('made_in'),
                ])
                
                product.refresh_from_db()
                

            # Redireciona para a página de detalhes do produto após a atualização
            return redirect('/')
        
        except Exception as e:
            print(f"exception {e}")
            raise e
            messages.error(request, f"Erro ao atualizar o produto: {e}")
            return render(request, "fla_loja/edit_product.html", {"product": data})

    return render(request, 
                  "fla_loja/edit_product.html", 
                  {
                    'isLogged': request.session.get('isLogged', False),
                    'isEmployee': request.session.get('isEmployee', False),
                    "product": data
                    }
                )


def edit_product_old(request, _id):
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
        
        return render(
            request, 
            "fla_loja/edit_product.html", 
            {
                'isLogged': request.session.get('isLogged', False),
                'isEmployee': request.session.get('isEmployee', False),
                "product": data
            }
        )


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
    
    # Verificar se há um pedido de remoção
    if request.method == 'POST':
        product_id = request.POST.get('remove_product_id')
        PurchasesNotCompleted.objects.filter(id_car=car.id, id_product=product_id).delete()
        return redirect('fla_loja:mycar')

    purchasesNotCompleted = PurchasesNotCompleted.objects.filter(id_car=car.id)
    
    product_map = {}
    total_price = 0
    
    for purchase in purchasesNotCompleted:
        product = Product.objects.get(pk=purchase.id_product.id)
        price_per_purchase = product.price * purchase.quantity

        # Verifica se o produto já está no dicionário
        if product.id in product_map:
            product_map[product.id]['quantity'] += purchase.quantity
            product_map[product.id]['price_per_purchase'] += price_per_purchase
        else:
            product_map[product.id] = {
                'id': product.id,
                'image': product.image.url if product.image else None,
                'name': product.name,
                'quantity': purchase.quantity,
                'price_per_purchase': price_per_purchase,
            }
        
        total_price += price_per_purchase

    context = {
        'isLogged': request.session.get('isLogged', False),
        'isEmployee': request.session.get('isEmployee', False),
        'car': product_map.values(),  # Apenas os valores do dicionário
        'total_price': total_price
    }
    
    return render(request, 'fla_loja/mycar.html', context)


def myorders(request):
    cars = Car.objects.filter(id_client=request.session.get('id'))
    selected_month = request.GET.get('month')
    selected_year = request.GET.get('year')

    purchasesCompleted = PurchasesCompleted.objects.all()

    purchased_products_dict = []

    for purchase in purchasesCompleted:
        for car in cars:
            # Verifique se a venda é do cliente e se o status não é 'Pagamento pendente'
            if purchase.id_car.id == car.id:
                product = Product.objects.get(pk=purchase.id_product.id)
                sale_date = car.date

                # Filtrar por mês e ano, se selecionados
                if (not selected_month or sale_date.month == int(selected_month)) and \
                   (not selected_year or sale_date.year == int(selected_year)):

                    # Calcular o preço total com desconto
                    discount = car.cupomPercent / 100 if car.cupomPercent else 0
                    price_after_discount = product.price * (1 - discount)

                    # Verificar se já existe um produto com o mesmo ID e preço após o desconto
                    found = False
                    for item in purchased_products_dict:
                        if item['id'] == product.id and item['price'] == price_after_discount:
                            item['quantity'] += purchase.quantity
                            found = True
                            break

                    # Se não encontrado, adicionar um novo produto ao dicionário
                    if not found:
                        purchased_products_dict.append({
                            'id': product.id,
                            'name': product.name,
                            'quantity': purchase.quantity,
                            'price': price_after_discount,
                            'image': product.image.url if product.image else None,
                            'status': car.status
                        })

    context = {
        'isLogged': request.session.get('isLogged', False),
        'isEmployee': request.session.get('isEmployee', False),
        'purchased_products': purchased_products_dict,
        'months': range(1, 13),  # Adicione os meses disponíveis
        'years': range(2020, datetime.today().year + 1),  # Ajuste conforme necessário
        'selected_month': selected_month,
        'selected_year': selected_year
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
        cupom = request.POST.get('cupom', '').upper().strip()
        
        purchasesNotCompleted = PurchasesNotCompleted.objects.all()
    
        errors = False
        total_price = 0
        
        for purchase in purchasesNotCompleted:
            if purchase.id_car.id == car.id:
                product = Product.objects.get(pk=purchase.id_product.id)
                if product.quantity_in_stock - purchase.quantity <= 0:
                    messages.error(request, "Quantidade solicitada excede o estoque disponível.")
                    errors = True 
                    break
                
                price_per_purchase = product.price * purchase.quantity
                total_price += price_per_purchase

        if cupom:
            if cupom in CUPONS:
                discount = CUPONS[cupom]
                total_price *= (1 - discount)
                car.cupomPercent = discount * 100  # Atribui o percentual de desconto do cupom
            else:
                messages.error(request, "Cupom inválido.")  
                errors = True
        else:
            car.cupomPercent = 0  # Quando nenhum cupom é inserido

        if errors:
            return redirect('fla_loja:mycar')
        
        
        car.id_employee = employee
        car.payment_method = payment_method
        car.date = datetime.today().strftime('%Y-%m-%d')
        car.status = "Compra finalizada"
        car.save()
        
        employee.sales_count += total_price
        employee.save()
        
        # Atualiza o estoque e cria registros de compras finalizadas
        for purchase in purchasesNotCompleted:
            if purchase.id_car.id == car.id:
                product = Product.objects.get(pk=purchase.id_product.id)
                product.quantity_in_stock -= purchase.quantity
                product.save()
                PurchasesCompleted.objects.create(
                    id_car=car,
                    id_product=product,
                    quantity=purchase.quantity
                )
                
                purchase.delete()


        Car.objects.create(
            id_client=Client.objects.get(pk=request.session.get('id')),
            status='Carrinho atual',
            date=datetime.today().strftime('%Y-%m-%d')
        )

        return redirect('fla_loja:index')


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
    # Obtenha os parâmetros de filtragem do request
    selected_month = request.GET.get('month')
    selected_year = request.GET.get('year')

    # Filtrar os registros de vendas
    cars = Car.objects.filter(id_employee=request.session.get('id'))
    purchasesCompleted = PurchasesCompleted.objects.all()

    # Dicionário para armazenar produtos agrupados
    purchased_products_dict = {}
    total_sales = 0
    total_quantity = 0  # Variável para armazenar a quantidade total de produtos vendidos

    for purchase in purchasesCompleted:
        for car in cars:
            # Verifique se a venda é do funcionário e se o status não é 'Pagamento pendente'
            if purchase.id_car.id == car.id:
                product = Product.objects.get(pk=purchase.id_product.id)
                sale_date = car.date

                # Calcular o preço com o desconto aplicado (se houver)
                discount = car.cupomPercent if car.cupomPercent else 0
                discounted_price = product.price * (1 - discount / 100)

                # Filtrar por mês e ano, se selecionados
                if (not selected_month or sale_date.month == int(selected_month)) and \
                   (not selected_year or sale_date.year == int(selected_year)):
                    total_sales += purchase.quantity * discounted_price
                    total_quantity += purchase.quantity  # Atualize a quantidade total

                    # Use o ID do produto e o preço como chave para distinguir produtos com preços diferentes
                    product_key = f'{product.id}_{discounted_price}'

                    if product_key in purchased_products_dict:
                        purchased_products_dict[product_key]['quantity'] += purchase.quantity
                    else:
                        purchased_products_dict[product_key] = {
                            'name': product.name,
                            'quantity': purchase.quantity,
                            'price': discounted_price,
                            'image': product.image.url if product.image else None,
                            'status': car.status
                        }

    # Transformar dicionário em lista
    purchased_products = [
        {'id': product_key.split('_')[0], **details}
        for product_key, details in purchased_products_dict.items()
    ]

    context = {
        'isLogged': request.session.get('isLogged', False),
        'isEmployee': request.session.get('isEmployee', False),
        'purchased_products': purchased_products,
        'total_sales': total_sales,
        'total_quantity': total_quantity,  # Adicione a quantidade total ao contexto
        'months': range(1, 13),  # Adicione os meses disponíveis
        'years': range(2020, datetime.today().year + 1),  # Ajuste conforme necessário
        'selected_month': selected_month,
        'selected_year': selected_year
    }

    return render(request, 'fla_loja/my_sales.html', context)


# +++++++++++++++++++++++++++++++++++++  Sales  +++++++++++++++++++++++++++++++++++++
@api_view(['GET'])
def sales(request):
    # Obtenha os parâmetros de filtragem do request
    selected_month = request.GET.get('month')
    selected_year = request.GET.get('year')

    # Obter todas as vendas completadas
    cars = Car.objects.all()  # Excluir os carrinhos com pagamento pendente
    purchasesCompleted = PurchasesCompleted.objects.all()

    # Dicionário para armazenar produtos agrupados
    purchased_products_dict = {}
    total_sales = 0
    total_quantity_sold = 0  # Variável para armazenar o total de unidades vendidas

    for purchase in purchasesCompleted:
        for car in cars:
            if purchase.id_car.id == car.id:
                product = Product.objects.get(pk=purchase.id_product.id)
                sale_date = car.date

                # Aplicar desconto se houver cupom
                discount_percentage = car.cupomPercent if car.cupomPercent else 0
                discounted_price = product.price * (1 - discount_percentage / 100)

                # Filtrar por mês e ano, se selecionados
                if (not selected_month or sale_date.month == int(selected_month)) and \
                   (not selected_year or sale_date.year == int(selected_year)):
                    total_sales += purchase.quantity * discounted_price
                    total_quantity_sold += purchase.quantity  # Incrementa a quantidade de produtos vendidos
                    
                    # Agrupar produtos pelo ID e preço
                    product_key = f'{product.id}_{discounted_price}'
                    if product_key in purchased_products_dict:
                        purchased_products_dict[product_key]['quantity'] += purchase.quantity
                    else:
                        purchased_products_dict[product_key] = {
                            'name': product.name,
                            'quantity': purchase.quantity,
                            'price': discounted_price,
                            'image': product.image.url if product.image else None,
                            'status': car.status
                        }

    # Transformar dicionário em lista
    purchased_products = [
        {'id': product_key.split('_')[0], **details}
        for product_key, details in purchased_products_dict.items()
    ]

    context = {
        'isLogged': request.session.get('isLogged', False),
        'isEmployee': request.session.get('isEmployee', False),
        'purchased_products': purchased_products,
        'total_sales': total_sales,
        'total_quantity_sold': total_quantity_sold,  # Adicionar ao contexto
        'months': range(1, 13),  # Adicione os meses disponíveis
        'years': range(2020, datetime.today().year + 1),  # Ajuste conforme necessário
        'selected_month': selected_month,
        'selected_year': selected_year
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
        cupom = request.POST.get("cupom", "").upper().strip()
        date_purchased = datetime.today().strftime('%Y-%m-%d')
        status = 'Compra finalizada'

        client = Client.objects.get(pk=client_id)
        employee = Employee.objects.get(pk=employee_id)
        
        errors = False
        if not client or not employee:
            messages.error(request, "Cliente ou Vendedor inválido.")
            errors = True
        
        
        if quantity > product.quantity_in_stock:
            messages.error(request, "Quantidade solicitada excede o estoque disponível.")
            errors = True

        # Verificar se o cupom foi inserido
        if cupom:
            if cupom in CUPONS:
                discount = CUPONS[cupom]
            else:
                messages.error(request, "Cupom inválido.")
                return render(request, 'fla_loja/sale.html', {'product': product})
        else:
            discount = 0

        # Calcula o preço total com desconto (se houver)
        total_price = quantity * product.price * (1 - discount)
        
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
            payment_method=payment_method,
            cupomPercent=discount * 100
        )
        
        last_car = Car.objects.last()

        PurchasesCompleted.objects.create(
            id_car=last_car,
            id_product=product,
            quantity=quantity
        )

        product.quantity_in_stock -= quantity
        product.save()

        employee.sales_count += total_price
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


def popular_products(request):
    # Agrupar as compras pelo produto e contar quantas vezes cada produto foi comprado
    produtos_agrupados = PurchasesCompleted.objects.values('id_product').annotate(total_compras=Count('id_product')).order_by('-total_compras')[:3]

    # Pegar os objetos de produto reais para exibir mais informações (ex.: nome)
    produtos_populares = []
    for item in produtos_agrupados:
        produto = Product.objects.get(id=item['id_product'])
        produtos_populares.append({
            'produto': produto,
            'total_compras': item['total_compras']
        })

    context = {
        'isLogged': request.session.get('isLogged', False),
        'isEmployee': request.session.get('isEmployee', False),
        'all_products': produtos_populares
    }
    
    return render(request, 'fla_loja/produtos_populares.html', context)
