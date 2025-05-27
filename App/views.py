from weasyprint import HTML

from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.db import transaction
from django.db.models import Prefetch
from django.template.loader import render_to_string
from django.core.cache import cache

from .services.session_cache import get_all_products, get_all_quotes, generate_temp_id
from .services.utils import calcultate_subtotal, remove_item_from_subtotal

from .models import Quote, Product, ProductQuote, Template, TemplateProduct

from .forms import QuoteForm, ProductQuoteForm, PricingForm, ProductQuoteFullForm

from .Constants.logo import OLYMPUS_LOGO


def Index(request):
    """
    Entry view for the web app.

    Redirects authenticated users to the home dashboard,
    otherwise renders the index page.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: Redirect or rendered HTML page.
    """
    email = request.session.get("user_email")
    name = request.session.get("full_name")
    if name and email:
        return redirect("home")
    return render(request, 'index.html')


def dashboard_view(request):
    context = {
        "user_email": request.session.get("user_email"),
        "full_name": request.session.get("full_name")
    }
    return render(request, 'home.html', context=context)


def list_layout_view(request):
    return render(request, "quote/list_layout.html")


def quote_list_view(request):
    quotes = get_all_quotes()

    id = request.GET.get("public_id")
    client = request.GET.get("client")
    date = request.GET.get("date")

    if id:
        quotes = quotes.filter(public_id__icontains=id)
    if client:
        quotes = quotes.filter(client__entity__name__icontains=client)
    if date:
        quotes = quotes.filter(date=date)

    return render(request, "quote/partials/quote_list.html", {'quotes': quotes})


def quote_products_view(request, pk):
    products = ProductQuote.objects.filter(quote__pk=pk)
    return render(request, "quote/partials/product_by_quote.html", {"products": products})


def product_form_view(request):
    pk = request.GET.get("product-form")
    
    index = request.session["form_counter"]
    request.session["form_counter"] += 1

    if int(index) >= 10:
        return HttpResponse("")
    
    if pk:
        instance = ProductQuote.objects.get(pk=pk)
    else:
        instance = None

    product_form = ProductQuoteForm(index=index, instance=instance) 
    products = get_all_products()

    context = {
        "index": index,
        "product_pk": pk,
        "product_form": product_form,
        "products": products
    }

    return render(request, "quote/partials/product_form.html", context=context)


def product_form_from_template_view(request):
    pk = request.GET.get("product-form")
    
    index = request.session["form_counter"]
    request.session["form_counter"] += 1

    if int(index) >= 10:
        return HttpResponse("")
    
    if pk:
        try:
            product = TemplateProduct.objects.get(pk=pk).product
            initial = {
                'product': product,
                'unit_price': product.price,
            }
        except Product.DoesNotExist:
            initial = None

    product_form = ProductQuoteForm(index=index, initial=initial) 
    products = get_all_products()
    context = {
        "index": index,
        "product_pk": pk,
        "product_form": product_form,
        "products": products
    }

    return render(request, "quote/partials/product_form.html", context=context)


def remove_product_form_view(request):
    request.session["form_counter"] -= 1
    index = request.GET.get("product_pk")
    remove_item_from_subtotal(request, index)
    
    return HttpResponse("")


def update_product_prices_view(request):
    form_counter = request.GET.get("index", 0)
    product = request.GET.get("product")
    discount = int(request.GET.get("discount"))
    quantity = int(request.GET.get("quantity"))
    profit_margin = 35

    if not product:
        return HttpResponse("")
    
    product = Product.objects.get(pk=product)

    unit_price, subtotal = calcultate_subtotal(request, form_counter, product, discount, profit_margin, quantity)

    pricing_form = PricingForm(initial={"unit_price": unit_price, "subtotal": subtotal}, index=form_counter)

    context = {
        "index": form_counter,
        "pricing_form": pricing_form,
        "subtotal": subtotal
    }
    return render(request, "quote/partials/prices.html", context=context)


def update_quote_totals_view(request):
    # The burst is too fast, we need another logic
    # Actually, the view is called too fast, so it doesn't let it load properly
    current_total = cache.get('total_net', {})

    total_net = sum([value for value in current_total.values()])

    iva = round(total_net * 0.19)
    final = total_net + iva

    context = {
        'total_net': total_net,
        'iva': iva,
        'final': final,
    }
    
    return render(request, "quote/partials/total_prices.html", context=context)


def quote_detail_view(request, pk):
    quote = Quote.objects.get(pk=pk)
    iva = round(quote.total * 0.19)
    final = quote.total + iva
    return render(request, 'quote/partials/overview.html', {'quote': quote, 'iva': iva, 'final': final,})


def quote_create_view(request):
    cache.set('total_net', {})
    context = {}
    if request.method == "POST":
        public_id = request.POST.get("public_id")
        client = request.POST.get("client") or 1
        salesRep = request.POST.get("salesRep") or 1
        items = []
        keys = ['product', 'discount', 'unit_price', 'quantity', 'subtotal']
        length = len(request.POST.getlist('product'))

        for i in range(length):
            item = {key: request.POST.getlist(key)[i] for key in keys}
            item['profit_margin'] = 35
            items.append(item)

        try:
            with transaction.atomic():
                quote_form = QuoteForm({"public_id":public_id, "client":client, "salesRep": salesRep})
                if quote_form.is_valid():
                    quote = quote_form.save()
                    print(f"Quote #{quote.public_id} saved!")


                for item in items:
                    item["quote"] = quote.pk
                    product_quote_form = ProductQuoteFullForm(item)
                    if product_quote_form.is_valid():
                        product_quote = product_quote_form.save()
                        print(f"Product quote #{product_quote.pk} related to Quote #{quote.public_id} saved!")
            
            return redirect("dashboard")

        except Exception as e:
            print("Transaction failed:", e)
            print("Changes reverted.")

    request.session["form_counter"] = 0
    request.session["total_net"] = {}
    quote_form = QuoteForm(initial={'public_id': generate_temp_id()})
    context['quote_form'] = quote_form
    return render(request, "quote/partials/create.html", context=context)


def quote_update_view(request, pk):
    cache.set('total_net', {})
    quote = get_object_or_404(
        Quote.objects.prefetch_related(
            Prefetch(
                'products',
                queryset=ProductQuote.objects.only('pk')
            )
        ),
        pk=pk
    )
    if request.method == "POST":
        public_id = request.POST.get("public_id")
        client = request.POST.get("client")
        salesRep = request.POST.get("salesRep")
        items = []
        keys = ['product', 'discount', 'unit_price', 'quantity', 'subtotal', 'product_pk']
        length = len(request.POST.getlist('product'))

        for i in range(length):
            item = {key: request.POST.getlist(key)[i] for key in keys}
            item['profit_margin'] = 35
            items.append(item)

        try:
            with transaction.atomic():
                quote_form = QuoteForm({"public_id":public_id, "client":client, "salesRep": salesRep}, instance=quote)
                if quote_form.is_valid():
                    quote = quote_form.save()
                    print(f"Quote #{quote.public_id} saved!")


                for item in items:
                    item["quote"] = quote.pk
                    product_pk = item.pop("product_pk")
                    if product_pk and str(product_pk).isdigit():
                        instance = ProductQuote.objects.get(pk=product_pk)
                    else:
                        instance = None
                    product_quote_form = ProductQuoteFullForm(item, instance=instance)
                    if product_quote_form.is_valid():
                        product_quote = product_quote_form.save()
                        print(f"Product quote #{product_quote.pk} related to Quote #{quote.public_id} saved!")
            
            return redirect("dashboard")

        except Exception as e:
            print("Transaction failed:", e)
            print("Changes reverted.")

    
    request.session["form_counter"] = 0
    request.session["total_net"] = {}
    quote_form = QuoteForm(instance=quote)
    products_pks = list(quote.products.values_list("pk", flat=True))
    context = {
        'quote_form': quote_form,
        'pk': pk,
        'product_pks': products_pks
    }
    return render(request, "quote/partials/update.html", context=context)


def quote_delete_view(request, pk):
    quote = get_object_or_404(Quote, pk=pk).delete()
    print(f"Quote #{quote} deleted")
    return redirect("list_layout")


def template_selector_view(request):
    templates = Template.objects.all()
    return render(request, "quote/partials/template_selector.html", {'templates': templates})


def template_products_view(request):
    template = request.GET.get("template")
    template = Template.objects.get(pk=template)
    products_pks = list(template.template_products.values_list("pk", flat=True))
    return render(request, "quote/partials/template_products.html", {'products_pks': products_pks})


def generate_quote_pdf_view(request, quote_id):
    quote = Quote.objects.get(id=quote_id)
    products = ProductQuote.objects.filter(quote=quote)
    iva = round(quote.total * 0.19)
    final = quote.total + iva

    html_string_pdf = render_to_string(
        "docs/quote.html",
        {
            'quote': quote,
            'iva': iva,
            'final': final,
            'products': products,
            'logo': OLYMPUS_LOGO,
        }
    )
    pdf = HTML(string=html_string_pdf).write_pdf()
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Cotizacion #{quote.public_id} - {quote.client.entity.name}.pdf"'
    return response