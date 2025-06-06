from django.contrib import admin
from .models import Message, Order, Product

# Register your models here.

admin.site.register(Message)
admin.site.register(Order)
admin.site.register(Product)