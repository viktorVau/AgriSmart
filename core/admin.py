from django.contrib import admin
from .models import Farmer, Agronomist, SoilTest

# Register your models here.
admin.site.register(Farmer)
admin.site.register(Agronomist)
admin.site.register(SoilTest)