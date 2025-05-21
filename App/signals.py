from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import ProductQuote


@receiver(post_save, sender=ProductQuote)
def update_quote_total(sender, instance, **kwargs):
    print("Quote signal activated!")
    quote = instance.quote
    total = sum(product.subtotal for product in quote.products.all())
    quote.total = total
    quote.save()
