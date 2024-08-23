from django.contrib import admin

from .models import *

admin.site.register(Client)
admin.site.register(Employee)
admin.site.register(Sale)
admin.site.register(Shopping)
admin.site.register(Product)