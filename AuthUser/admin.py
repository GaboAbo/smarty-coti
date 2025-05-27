from django.contrib import admin

from .models import Entity, Client, SalesRep

# Register your models here.
admin.site.register(Entity)
admin.site.register(Client)
admin.site.register(SalesRep)