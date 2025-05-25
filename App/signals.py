from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache

from .models import Product, Quote, ProductQuote


@receiver(post_save, sender=ProductQuote)
def update_quote_total(sender, instance, **kwargs):
    print("Quote signal activated!")
    quote = instance.quote
    total = sum(product.subtotal for product in quote.products.all())
    quote.total = total
    quote.save()


@receiver(post_save, sender=Product)
@receiver(post_delete, sender=Product)
def clear_product_cache(sender, **kwargs):
    cache.delete("all_products")


@receiver(post_save, sender=Quote)
@receiver(post_delete, sender=Quote)
def clear_quote_cache(sender, **kwargs):
    cache.delete("all_quotes")
