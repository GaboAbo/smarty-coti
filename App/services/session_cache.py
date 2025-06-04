import random, time

from django.core.cache import cache

from ..models import Product, Quote


def get_all_products(refresh=None):
    products = cache.get("all_products")
    if products is None or refresh:
        products = Product.objects.all()
        cache.set("all_products", products, timeout=None)
    return products


def get_all_quotes(pk=None, role="REP", refresh=None):
    quotes = cache.get("all_quotes")
    if quotes is None or refresh:
        if role == "MAN" or role == "ADM":
            quotes = Quote.objects.all()
        else:
            quotes = Quote.objects.filter(salesRep__pk=pk)
        cache.set("all_quotes", quotes, timeout=None)
    return quotes


def generate_temp_id():
    return f"{int(time.time())}{random.randint(0, 999999)}"
