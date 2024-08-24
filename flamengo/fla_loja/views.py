from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.template import loader

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .models import *
from .serializer import *

import json


@api_view(['GET'])
def index(request):
    all_products = Product.objects.all()
    template = loader.get_template("fla_loja/index.html")
    context = {
        "all_products": all_products,
    }
    return HttpResponse(template.render(context, request))


@api_view(['GET', 'PUT'])
def get_product_by_name(request, nick):
  try:
    product = Product.objects.get(pk=nick)
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