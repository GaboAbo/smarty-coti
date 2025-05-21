from django.contrib import admin

from .models import Entity, Client, SalesRep, Group, Product, ProductQuote, Quote


# Register your models here.
admin.site.register(Entity)
admin.site.register(Client)
admin.site.register(SalesRep)
admin.site.register(Group)
admin.site.register(Product)
admin.site.register(ProductQuote)
admin.site.register(Quote)