from weasyprint import HTML

from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.db import transaction, IntegrityError
from django.template.loader import render_to_string
from django.core.paginator import Paginator
from django.core.cache import cache
from django.contrib.auth.decorators import login_required

from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods

from .services.session_cache import set_indicators, get_all_products, get_all_quotes
from .services.utils import exchange_currency, set_total_net, calculate_subtotal, remove_item_from_subtotal, calculate_quote_totals

from .models import Quote, Product, ProductQuote, Template, TemplateProduct

from AuthUser.models import SalesRep, Entity

from .forms import QuoteForm, ProductQuoteForm, PricingForm, ProductQuoteFullForm

from .Constants.logo import OLYMPUS_LOGO
from .Constants.bg import BACKGROUND


def index(request):
    if request.session.get("user_email"):
        return redirect("dashboard")
    
    return render(request, 'index.html', {'bg': BACKGROUND})


def dashboard_view(request):
    if not request.session.get("user_email"):
        return redirect("/")

    set_indicators()
    role = request.session.get("role")
    role_display = dict(SalesRep.ROLE_CHOICES).get(role, "Invitado")
    
    context = {
        "user_email": request.session.get("user_email"),
        "full_name": request.session.get("full_name"),
        "role": request.session.get("role"),
        "role_display": role_display
    }
    return render(request, 'home.html', context=context)


def sidebar(request):
    """
    Renders the sidebar with active tab highlight.

    Args:
        request (HttpRequest): The HTTP request object. May contain `tab` GET param.

    Returns:
        HttpResponse: Rendered sidebar partial.
    """
    tab = request.GET.get("tab", "quotes")
    return render(request, "partials/sidebar.html", {"active_tab": tab})


def list_layout_view(request):
    context = {
        "role": request.session.get("role"),
    }
    return render(request, "quote/list_layout.html", context=context)


def quote_list_view(request):
    user_pk = request.session.get("pk")
    user_role = request.session.get("role")
    refresh = request.GET.get("refresh") or None

    quotes = get_all_quotes(user_pk, user_role, refresh).order_by("date")

    pk = request.GET.get("pk")
    client = request.GET.get("client")
    sales_rep = request.GET.get("sales_rep")
    date = request.GET.get("date")
    status = request.GET.get("status")

    if pk:
        quotes = quotes.filter(pk__icontains=pk)
    if client:
        quotes = quotes.filter(client__entity__name__icontains=client)
    if sales_rep:
        quotes = quotes.filter(salesRep__name__icontains=sales_rep)
    if date:
        quotes = quotes.filter(date=date)
    if status:
        quotes = quotes.filter(status=status)

    paginator = Paginator(quotes, 10)
    page_number = request.GET.get("page", 1) or 1
    page_obj = paginator.get_page(page_number)

    real_quotes = quotes.exists()

    quotes = list(page_obj.object_list)
    quotes += [None] * (10 - len(quotes))

    context = {
        "quotes": quotes,
        "real_quotes": real_quotes,
        "page_obj": page_obj,
        "current_filters": request.GET.urlencode(),
    }

    return render(request, "quote/partials/quote_list.html", context=context)
    

def pending_quote_list_view(request):
    user_pk = request.session.get("pk")
    user_role = request.session.get("role")
    refresh = request.GET.get("refresh") or None

    quotes = get_all_quotes(user_pk, user_role, refresh).filter(status="WT").order_by("date")

    pk = request.GET.get("pk")
    client = request.GET.get("client")
    sales_rep = request.GET.get("sales_rep")
    date = request.GET.get("date")
    status = request.GET.get("status")

    if pk:
        quotes = quotes.filter(pk__icontains=pk)
    if client:
        quotes = quotes.filter(client__entity__name__icontains=client)
    if sales_rep:
        quotes = quotes.filter(salesRep__name__icontains=sales_rep)
    if date:
        quotes = quotes.filter(date=date)
    if status:
        quotes = quotes.filter(status=status)

    paginator = Paginator(quotes, 10)
    page_number = request.GET.get("page", 1) or 1
    page_obj = paginator.get_page(page_number)

    real_quotes = quotes.exists()

    quotes = list(page_obj.object_list)
    quotes += [None] * (10 - len(quotes))

    context = {
        "quotes": quotes,
        "real_quotes": real_quotes,
        "page_obj": page_obj,
        "current_filters": request.GET.urlencode(),
    }

    return render(request, "quote/partials/quote_list.html", context=context)


def quote_view(request, pk):
    quote = Quote.objects.get(pk=pk)

    return render(request, "quote/partials/quote.html", {"quote": quote})


def set_quote_status_view(request, pk, status):
    user_pk = request.session.get("pk")
    user = get_object_or_404(SalesRep, pk=user_pk)
    quote = get_object_or_404(Quote, pk=pk)

    quote = Quote.objects.get(pk=pk)
    if status == "AP":
        quote.approve_by_manager(user)
    elif status == "RJ":
        quote.reject(user)
    elif status == "CL":
        quote.close()

    return render(request, "quote/list_layout.html")
    

def quote_products_view(request, pk):
    role = request.session.get("role")
    products = ProductQuote.objects.filter(quote__pk=pk)

    paginator = Paginator(products, 6)
    page_number = request.GET.get("page", 1) or 1
    page_obj = paginator.get_page(page_number)

    products = list(page_obj.object_list)
    products += [None] * (6 - len(products))

    context = {
        "pk": pk,
        "role": role,
        "products": products,
        "page_obj": page_obj,
    }

    return render(request, "quote/partials/product_by_quote.html", context=context)


def product_form_view(request):
    role = request.session.get("role")
    pk = request.GET.get("pk")
    index = cache.get("form_counter", 0) + 1

    exchage = request.GET.get("exchage") or "USD"

    cache.set("form_counter", index)
    
    if pk:
        instance = ProductQuote.objects.get(pk=pk)
        instance.price = exchange_currency(instance.price, exchage)
    else:
        instance = None

    product_form = ProductQuoteForm(index=index, instance=instance)

    context = {
        "role": role,
        "index": index,
        "product_pk": pk,
        "product_form": product_form,
    }

    return render(request, "quote/partials/product_form.html", context=context)


def product_form_from_template_view(request):
    role = request.session.get("role")
    pk = request.GET.get("product-form")
    
    index = cache.get("form_counter", 0)
    cache.set("form_counter", index + 1)

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
        "role": role,
        "index": index,
        "product_pk": pk,
        "product_form": product_form,
        "products": products
    }

    return render(request, "quote/partials/product_form.html", context=context)


def remove_product_form_view(request):
    cache.set("form_counter", cache.get("form_counter", 0) - 1)
    index = request.GET.get("product_pk")
    remove_item_from_subtotal(request, index)
    
    return HttpResponse("")


def update_product_prices_view(request):
    form_counter = request.GET.get("index", 0)
    product = request.GET.get("product")
    quantity = request.GET.get("quantity", 1)
    discount = int(request.GET.get("discount", 0))
    profit_margin = int(request.GET.get("profit_margin", 35))

    exchange = request.GET.get("exchange") or "USD"

    if not product:
        return HttpResponse("")
    
    try:
        product = Product.objects.get(pk=product)
    except Product.DoesNotExist:
        return HttpResponse("")

    price = exchange_currency(product.price, exchange)

    unit_price, subtotal = calculate_subtotal(
        form_counter,
        price,
        int(discount),
        int(profit_margin),
        int(quantity)
    )

    if product.code == "MDO":
        custom = True
    else:
        custom = False

    if exchange == "CLP":
        unit_price = int(unit_price)
        subtotal = int(subtotal)

    pricing_form = PricingForm(initial={"unit_price": unit_price, "subtotal": subtotal}, index=form_counter, custom=custom)

    context = {
        "index": form_counter,
        "pricing_form": pricing_form,
        "subtotal": subtotal
    }
    return render(request, "quote/partials/prices.html", context=context)


def update_quote_totals_view(request):
    index = request.GET.get("index") or None
    price = request.GET.get("subtotal") or None
    exchange = request.GET.get("exchange") or None

    if index and price:
        set_total_net(index, price)

    context = calculate_quote_totals(exchange)
    return render(request, "quote/partials/total_prices.html", context=context)


def quote_detail_view(request, pk):
    role = request.session.get("role")
    quote = Quote.objects.get(pk=pk)

    context = {
        "role": role,
        "quote": quote,
    }

    return render(request, 'quote/partials/overview.html', context=context)


@csrf_protect
@require_http_methods(["GET", "POST"])
def quote_create_or_update_view(request):
    cache.set('total_net', {})

    pk = request.GET.get("pk") or None
    action = request.GET.get("action") or "create"

    if pk and action == "update":
        quote = get_object_or_404(
            Quote.objects.prefetch_related('products'),
            pk=pk
        )
    else:
        quote = None

    if request.method == "POST":
        client = request.POST.get("client") or Entity.objects.first().id
        salesRep = request.POST.get("salesRep") or SalesRep.objects.first().id
        currency = request.POST.get("exchange") or "USD"
        total_net = request.POST.get("total_net") or 0
        iva = request.POST.get("iva") or 0
        final = request.POST.get("final") or 0

        items = []
        keys = ['product', 'discount', 'profit_margin', 'unit_price', 'quantity', 'subtotal']
        if action == "update":
            keys.append("product_pk")
        
        length = len(request.POST.getlist('product'))

        for i in range(length):
            item = {key: request.POST.getlist(key)[i] for key in keys}
            items.append(item)

        try:
            with transaction.atomic():                    
                if action == "update":
                    quote_form = QuoteForm(
                        {
                            "client": client,
                            "salesRep": salesRep,
                            "currency": currency,
                            "total_net": total_net,
                            "iva": iva,
                            "final": final
                        },
                        instance=quote
                    )
                else:
                    quote_form = QuoteForm(
                        {
                            "client": client,
                            "salesRep": salesRep,
                            "currency": currency,
                            "total_net": total_net,
                            "iva": iva,
                            "final": final
                        }
                    )

                if quote_form.is_valid():
                    try:
                        quote = quote_form.save()
                        print(f"Quote #{quote.pk} saved.")
                    except IntegrityError as e:
                        print("IntegrityError while saving quote:", e)
                        raise
                    except Exception as e:
                        print("Unexpected error while saving quote:", e)
                        raise

                    for item in items:
                        item["quote"] = quote
                        try:
                            product_pk = int(item.pop("product_pk", None))
                        except (ValueError, TypeError):
                            product_pk = None
                        instance = ProductQuote.objects.filter(pk=product_pk).first() if product_pk else None
                        
                        product_quote_form = ProductQuoteFullForm(item, instance=instance)
                        if product_quote_form.is_valid():
                            print("form valid")
                            product_quote = product_quote_form.save()
                            print(f"Product quote #{product_quote.pk} related to Quote #{quote} saved!")

                    if quote.status == "WT" and not quote.has_discounted_items:
                        quote.status = "AP"
                        quote.approved_by = quote.salesRep
                        quote.save(update_fields=["status", "approved_by"])

            return redirect("dashboard")

        except Exception as e:
            print("Transaction failed:", e)
            print("Changes reverted.")

    request.session["form_counter"] = 0
    request.session["total_net"] = {}

    quote_form = QuoteForm(instance=quote)

    role = request.session.get("role")
    context = {
        "role": role,
        'quote_form': quote_form,
        'quote': quote,
        'pk': pk,
        'action': action,
    }

    if action == "update":
        products = quote.products.all()

        product_forms = [
            ProductQuoteForm(instance=product, index=index) for index, product in enumerate(products)
        ]

        context["product_forms"] = product_forms
        request.session["form_counter"] = len(products)

    return render(request, "quote/partials/create_or_update.html", context=context)


def quote_delete_view(request, pk):
    quote = get_object_or_404(Quote, pk=pk).delete()
    print(f"Quote #{quote} deleted")
    
    return render(request, "quote/list_layout.html")


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
    html_string_pdf = render_to_string(
        "docs/quote.html",
        {
            'quote': quote,
            'products': products,
            'logo': OLYMPUS_LOGO,
        }
    )
    pdf = HTML(string=html_string_pdf).write_pdf()
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Cotizacion #{quote} - {quote.client.name}.pdf"'
    return response