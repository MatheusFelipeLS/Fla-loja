from django.contrib import admin

from .models import *

admin.site.register(Client)
admin.site.register(Employee)
admin.site.register(Product)
admin.site.register(Car)
admin.site.register(PurchasesCompleted)
admin.site.register(PurchasesNotCompleted)