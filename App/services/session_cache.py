import random, time
from datetime import date

from django.core.cache import cache

from ..models import DailyIndicators

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
            quotes = Quote.objects.filter(salesRep__pk=pk).exclude(status="CL")
        cache.set("all_quotes", quotes, timeout=None)
    return quotes


def generate_temp_id():
    return f"{int(time.time())}{random.randint(0, 999999)}"


def set_indicators():
    today = date.today()
    try:
        indicators = DailyIndicators.objects.get(date=today)
        cache.set("indicators", indicators, timeout=60 * 60 * 24)
        return True
    except DailyIndicators.DoesNotExist:
        return False