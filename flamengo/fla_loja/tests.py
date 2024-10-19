from django.test import TestCase

# <!-- {% extends 'fla_loja/base.html' %}

# {% block content %}
# <main class="main main--stock" style="padding: 20px; margin-bottom: 14rem;">

#   <div class="table-responsive" style="margin-top: 3rem;">
#     {% if isEmployee %}
#     <h4 style="margin-bottom: 3rem;">O total em vendas foi R$ {{total_sales}}</h4>
#     {% endif %}
#     <table class="table table-bordered table-striped">
#       <thead class="table-dark" style="background-color: black; color: red;">
#         <tr>
#           <th scope="col">ID da compra</th>
#           <th scope="col">Foto do Produto</th>
#           <th scope="col">Nome do Produto</th>
#           <th scope="col">Preço pelas unidades</th>
#           <th scope="col">Unidades</th>
#           {% if not isEmployee %}
#           <th scope="col">Status</th>
#           {% endif  %}
#         </tr>
#       </thead>
#       <tbody>
#         {% for purshase in purshased_products %}
#         <tr>
#           <td>{{ purshase.id }}</td>
#           <td>
#             {% if purshase.image %}
#               <img src="{{ purshase.image }}" alt="{{ purshase.name }}" style="max-width: 100px;">
#             {% else %}
#               <span>N/A</span>
#             {% endif %}
#           </td>
#           <td>{{ purshase.name }}</td>
#           <td>R$ {{ purshase.price }} por unidade</td>
#           <td>{{ purshase.quantity }}</td>
#           {% if not isEmployee %}
#             {% if purshase.status == 'Pagamento pendente' %}
#               <td><a href="{% url 'fla_loja:paycar' purshase.id %}" class="btn btn-primary">Pagar</a></td>
#             {% else %}
#               <td>{{ purshase.status }}</td>
#             {% endif %}
#           {% endif %}
#           </tr>
#         {% empty %}
#         <tr>
#           <td colspan="5">Nenhum produto disponível.</td>  <- Atualize a coluna colspan para 5 ->
#         </tr>
#         {% endfor %}
#       </tbody>
#     </table>
#   </div>
# </main>
# {% endblock %} -->