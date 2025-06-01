from django.urls import path

from App.views import (
    index,
    sidebar,

    dashboard_view,
    list_layout_view,
    quote_list_view,
    pending_quote_list_view,
    quote_view,
    set_quote_status_view,
    product_form_view,
    product_form_from_template_view,
    remove_product_form_view,
    update_product_prices_view,
    update_quote_totals_view,
    quote_detail_view,
    quote_create_view,
    quote_update_view,
    quote_products_view,
    quote_delete_view,
    template_selector_view,
    template_products_view,
    generate_quote_pdf_view,
)

urlpatterns = [
    path('', index, name='index'),
    path('dashboard', dashboard_view, name='dashboard'),
    path('sidebar', sidebar, name='sidebar'),

    path('list-layout/', list_layout_view, name='list_layout'),
    path('quotes/', quote_list_view, name='quote_list'),
    path('pending_quotes/', pending_quote_list_view, name='pending_quote_list'),
    path('set_quote_status/<int:pk>/<str:status>/<place:str>', set_quote_status_view, name='set_status'),
    path('quote/<int:pk>', quote_view, name='quote'),

    path('product-form/', product_form_view, name='product_form'),
    path('product-form-from-template/', product_form_from_template_view, name='product_form_from_template'),
    path('remove-product-form/', remove_product_form_view, name='remove_product_form'),
    path('update-product-prices/', update_product_prices_view, name='update_product_prices'),
    path('update-quote-totals/', update_quote_totals_view, name='update_quote_totals'),

    path('quotes/create/', quote_create_view, name='create_quote'),
    path('quotes/<int:pk>/update/', quote_update_view, name='update_quote'),
    path('quotes/<int:pk>/', quote_detail_view, name='quote_detail'),
    path('quotes/<int:pk>/products/', quote_products_view, name='quote_products'),
    path('quotes/<int:pk>/delete/', quote_delete_view, name='delete_quote'),

    path('template-selector/', template_selector_view, name='template_selector'),
    path('template-products/', template_products_view, name='template_products'),

    path('quotes/<int:quote_id>/generate-pdf/', generate_quote_pdf_view, name='generate_pdf'),
]
