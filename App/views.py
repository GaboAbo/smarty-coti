from weasyprint import HTML

from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.db import transaction
from django.db.models import Prefetch
from django.template.loader import render_to_string

from .services.session_cache import get_all_products, get_all_groups, generate_temp_id

from .models import Quote, Product, ProductQuote

from .forms import QuoteForm, ProductQuoteForm, PricingForm, ProductQuoteFullForm

from .Constants.logo import OLYMPUS_LOGO

FREIGHT = 0.04
INSURANCE = 0.02
CUSTOMS = 0.02
WARRANT_AND_MAINTENANCE = 0.03


def calcultate_subtotal(request, index, product, discount, profit_margin, quantity):
    price_after_discount = round(product.price * ((100 - discount) / 100))
    price_after_percentages = round(price_after_discount * (1 + FREIGHT + INSURANCE + CUSTOMS + WARRANT_AND_MAINTENANCE))
    unit_price = round(price_after_percentages * ((100 + profit_margin) / 100))
    subtotal = unit_price * quantity

    total_net = request.session.get("total_net", {})
    total_net[f"total_net-{index}"] = subtotal
    request.session["total_net"] = total_net

    return unit_price, subtotal


def home_view(request):
    return render(request, "home.html", {})


def list_quotes(request):
    return render(request, "quote/list_layout.html")


def filter_quote(request):
    quotes = Quote.objects.all()
    id = request.GET.get("public_id")
    client = request.GET.get("client")
    date = request.GET.get("date")
    if id:
        quotes = quotes.filter(pk=id)
    if client:
        quotes = quotes.filter(client__name__icontains=client)
    if date:
        quotes = quotes.filter(date=date)
    return render(request, "quote/partials/filtered_list.html", {'quotes': quotes})


def products_by_quote(request, pk):
    products = ProductQuote.objects.filter(quote__pk=pk)
    return render(request, "quote/partials/product_by_quote.html", {"products": products})


def load_product_form(request):
    pk = request.GET.get("product-form")
    index = request.GET.get("index", None)
    
    if not index:
        index = request.session.get("form_counter")
        request.session["form_counter"] += 1

    if int(index) >= 10:
        return HttpResponse("")
    
    if pk:
        instance = ProductQuote.objects.get(pk=pk)
    else:
        instance = None

    product_form = ProductQuoteForm(index=index, instance=instance) 
    groups = get_all_groups()
    products = get_all_products()

    context = {
        "index": index,
        "product_pk": pk,
        "product_form": product_form,
        "groups": groups,
        "products": products
    }

    return render(request, "quote/partials/product_form.html", context=context)


def remove_product_form(request):
    request.session["form_counter"] -= 1
    return HttpResponse("")


def set_product_prices(request):
    form_counter = request.GET.get("index", 0)
    product = request.GET.get("product")
    discount = int(request.GET.get("discount"))
    profit_margin = int(request.GET.get("profit_margin"))
    quantity = int(request.GET.get("quantity"))

    if not product:
        return HttpResponse("")
    
    product = Product.objects.get(pk=product)

    unit_price, subtotal = calcultate_subtotal(request, form_counter, product, discount, profit_margin, quantity)

    pricing_form = PricingForm(initial={"unit_price": unit_price, "subtotal": subtotal}, index=form_counter)

    context = {
        "index": form_counter,
        "pricing_form": pricing_form
    }
    return render(request, "quote/partials/prices.html", context=context)


def set_total_prices(request):
    total_net = sum(int(total) for total in request.session["total_net"].values())
    iva = round(total_net * 0.19)
    final = total_net + iva

    context = {
        'total_net': total_net,
        'iva': iva,
        'final': final
    }
    
    return render(request, "quote/partials/total_prices.html", context=context)


def get_quote(request, pk):
    quote = Quote.objects.get(pk=pk)
    iva = round(quote.total * 0.19)
    final = quote.total + iva
    return render(request, 'quote/partials/overview.html', {'quote': quote, 'iva': iva, 'final': final,})


def create_quote(request):
    if request.method == "POST":
        public_id = request.POST.get("public_id")
        client = request.POST.get("client")
        salesRep = request.POST.get("salesRep")
        items = []
        keys = ['group', 'product', 'discount', 'profit_margin', 'unit_price', 'quantity', 'subtotal']
        length = len(request.POST.getlist('product'))

        for i in range(length):
            item = {key: request.POST.getlist(key)[i] for key in keys}
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
            
            return redirect("home")

        except Exception as e:
            print("Transaction failed:", e)
            print("Changes reverted.")

    request.session["form_counter"] = 0
    request.session["total_net"] = {}
    groups = get_all_groups()
    quote_form = QuoteForm(initial={'public_id': generate_temp_id()})
    return render(request, "quote/partials/create.html", {"groups": groups, 'quote_form': quote_form})


def update_quote(request, pk):
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
        keys = ['group', 'product', 'discount', 'profit_margin', 'unit_price', 'quantity', 'subtotal', 'product_pk']
        length = len(request.POST.getlist('product'))

        for i in range(length):
            item = {key: request.POST.getlist(key)[i] for key in keys}
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
            
            return redirect("home")

        except Exception as e:
            print("Transaction failed:", e)
            print("Changes reverted.")

    
    request.session["form_counter"] = (len(quote.products.all()))
    request.session["total_net"] = {}
    groups = get_all_groups()
    quote_form = QuoteForm(instance=quote)
    products_pks = list(quote.products.values_list("pk", flat=True))
    context = {
        "groups": groups,
        'quote_form': quote_form,
        'pk': pk,
        'product_pks': products_pks
    }
    return render(request, "quote/partials/update.html", context=context)


def generate_pdf(request, quote_id):
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
    response['Content-Disposition'] = f'attachment; filename="cotizacion_prueba.pdf"'
    return response