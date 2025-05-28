import random, time

from django.core.cache import cache

from ..models import Product, Quote


def get_all_products(pk=None, role="REP"):
    products = cache.get("all_products")
    if products is None:
        if role == "ADM":
            products = Product.objects.all()
        else:
            products = Product.objects.filter(salesRep__pk=pk)
        cache.set("all_products", products, timeout=None)
    return products


def get_all_quotes():
    quotes = cache.get("all_quotes")
    if quotes is None:
        quotes = Quote.objects.all()
        cache.set("all_quotes", quotes, timeout=None)
    return quotes


def generate_temp_id():
    return f"{int(time.time())}{random.randint(0, 999999)}"
