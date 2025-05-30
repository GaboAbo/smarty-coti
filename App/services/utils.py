from django.core.cache import cache

FREIGHT = 0.04
INSURANCE = 0.02
CUSTOMS = 0.02
WARRANT_AND_MAINTENANCE = 0.03


def calcultate_subtotal(request, index, product, discount, profit_margin, quantity):
    price_after_discount = round(product.price * ((100 - discount) / 100))
    price_after_percentages = round(price_after_discount * (1 + FREIGHT + INSURANCE + CUSTOMS + WARRANT_AND_MAINTENANCE))
    unit_price = round(price_after_percentages * ((100 + profit_margin) / 100))
    subtotal = unit_price * quantity

    current_total = cache.get('total_net', {})
    current_total[index] = subtotal
    cache.set('total_net', current_total)

    return unit_price, subtotal


def remove_item_from_subtotal(request, index):
    current_total = cache.get('total_net', {})
    current_total.pop(str(index))
    cache.set('total_net', current_total)

    pass


def calculate_quote_totals():
    current_total = cache.get('total_net', {})
    total_net = sum([value for value in current_total.values()])
    iva = round(total_net * 0.19)
    final = total_net + iva
    return {
        'total_net': total_net,
        'iva': iva,
        'final': final,
    }
