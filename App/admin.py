from django.contrib import admin

from .models import DailyIndicators, Product, ProductQuote, Quote, Template, TemplateProduct


# Register your models here.
admin.site.register(DailyIndicators)
admin.site.register(Product)
admin.site.register(ProductQuote)
admin.site.register(Quote)
admin.site.register(Template)
admin.site.register(TemplateProduct)
