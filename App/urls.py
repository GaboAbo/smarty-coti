from django.urls import path

from App.views import (
    home_view,
    list_quotes,
    filter_quote,
    load_product_form,
    remove_product_form,
    set_product_prices,
    set_total_prices,
    get_quote,
    create_quote,
    update_quote,
    products_by_quote,

    generate_pdf
)


urlpatterns = [
    path('', home_view, name='home'),

    path('list_quotes', list_quotes, name='list_quotes'),
    path('filter_quote', filter_quote, name='filter_quote'),
    path('load_product_form', load_product_form, name='load_product_form'),
    path('remove_product_form', remove_product_form, name='remove_product_form'),
    path('set_product_prices', set_product_prices, name='set_product_prices'),
    path('set_total_prices', set_total_prices, name='set_total_prices'),
    path('create_quote', create_quote, name='create_quote'),
    path('update_quote/<int:pk>', update_quote, name='update_quote'),
    path('get_quote/<int:pk>', get_quote, name='get_quote'),
    path('products_by_quote/<int:pk>', products_by_quote, name='products_by_quote'),

    path('generate_pdf/<int:quote_id>', generate_pdf, name='generate_pdf'),
]
