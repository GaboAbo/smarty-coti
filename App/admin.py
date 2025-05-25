from django.contrib import admin

from .models import Entity, Client, SalesRep, Product, ProductQuote, Quote, Template, TemplateProduct


# Register your models here.
admin.site.register(Entity)
admin.site.register(Client)
admin.site.register(SalesRep)
admin.site.register(Product)
admin.site.register(ProductQuote)
admin.site.register(Quote)
admin.site.register(Template)
admin.site.register(TemplateProduct)
