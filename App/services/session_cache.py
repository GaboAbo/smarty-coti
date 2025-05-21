import random, time

from django.core.cache import cache

from ..models import Product, Group


def get_all_products():
    products = cache.get("all_products")
    if products is None:
        products = Product.objects.all()
        cache.set("all_products", products, timeout=None)
    return products


def get_all_groups():
    groups = cache.get("all_groups")
    if groups is None:
        groups = Group.objects.all()
        cache.set("all_groups", groups, timeout=None)
    return groups


def generate_temp_id():
    return f"{int(time.time())}{random.randint(0, 999999)}"
