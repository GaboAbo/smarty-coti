from django.core.cache import cache
from django.core.cache import cache
from decimal import Decimal, InvalidOperation

from .session_cache import set_indicators

FREIGHT = Decimal(0.04)
INSURANCE = Decimal(0.02)
CUSTOMS = Decimal(0.02)
WARRANT_AND_MAINTENANCE = Decimal(0.03)


def exchange_currency(price, exchange: str):
    set_indicators()
    indicators = cache.get("indicators")
    
    if indicators is None:
        raise ValueError("Indicators not found in cache. Please ensure `set_indicators()` is called daily.")

    try:
        price = Decimal(price)
        dolar = Decimal(indicators.dolar)
        uf = Decimal(indicators.uf)
    except InvalidOperation:
        raise ValueError("Invalid values")

    exchange = exchange.upper()

    if exchange == "CLP":
        return round(price * dolar)
    elif exchange == "UF":
        return round((price * dolar) / uf, 4)
    else:
        return price


def calcultate_subtotal(request, index, price, discount, profit_margin, quantity):

    try:
        price = Decimal(price)
        discount = Decimal(discount)
        profit_margin = Decimal(profit_margin)
    except InvalidOperation:
        raise ValueError("Invalid values")

    price_after_discount = round(price * ((100 - discount) / 100), 2)
    price_after_percentages = round(price_after_discount * (1 + FREIGHT + INSURANCE + CUSTOMS + WARRANT_AND_MAINTENANCE), 2)
    unit_price = round(price_after_percentages * ((100 + profit_margin) / 100), 2)
    subtotal = unit_price * quantity

    current_total = cache.get('total_net', {})
    current_total[index] = subtotal
    cache.set('total_net', current_total)

    return unit_price, subtotal


def remove_item_from_subtotal(request, index):
    current_total = cache.get('total_net', {})
    item_subtotal = current_total.get(str(index))
    
    if item_subtotal:
        current_total.pop(str(index))
        cache.set('total_net', current_total)

    pass


def calculate_quote_totals():
    current_total = cache.get('total_net', {})
    total_net = sum([value for value in current_total.values()])
    iva = round(total_net * Decimal(0.19), 2)
    final = total_net + iva
    return {
        'total_net': total_net,
        'iva': iva,
        'final': final,
    }
