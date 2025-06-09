from django import forms
from .models import Quote, Product, ProductQuote, Template

from AuthUser.models import Entity, SalesRep


class TemplateForm(forms.ModelForm):

    class Meta:
        model = Template
        fields = ['name']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].widget.attrs.update({
            'class': 'w-full h-[24px] border-2 rounded-xs border-slate-300 focus:outline-none focus:border-slate-700 px-2 text-sm',
        })


class QuoteForm(forms.ModelForm):
    client = forms.ModelChoiceField(
        queryset=Entity.objects.all(),
        required=True,
        empty_label="Seleccione Institución",
        widget=forms.Select(attrs={
            'class': 'w-full h-[24px] border-2 rounded-xs border-slate-300 focus:outline-none focus:border-slate-700 px-2 text-sm',
            'list': 'client-list',
        })
    )

    salesRep = forms.ModelChoiceField(
        queryset=SalesRep.objects.all(),
        required=True,
        empty_label="Seleccione Rep. de Ventas",
        widget=forms.Select(attrs={
            'class': 'w-full h-[24px] border-2 rounded-xs border-slate-300 focus:outline-none focus:border-slate-700 px-2 text-sm',
            'list': 'client-list',
        })
    )

    currency = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full text-center',
        })
    )
    total_net = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'w-full text-center',
            'readonly': 'readonly',
            'style': 'pointer-events: none',
            'step': '0.0001',
        })
    )
    iva = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'w-full text-center',
            'readonly': 'readonly',
            'style': 'pointer-events: none',
            'step': '0.0001',
        })
    )
    final = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'w-full text-center',
            'readonly': 'readonly',
            'style': 'pointer-events: none',
            'step': '0.0001',
        })
    )

    class Meta:
        model = Quote
        fields = ['client', 'salesRep', 'currency', 'total_net', 'iva', 'final']


class ProductQuoteForm(forms.ModelForm):
    product = forms.ModelChoiceField(
        queryset=Product.objects.all(),
        required=True,
        widget=forms.Select(attrs={
            'list': 'product-list',
        })
    )

    discount = forms.IntegerField(
        min_value=0,
        max_value=100,
        initial=0,
        widget=forms.NumberInput(attrs={
            'step': '1',
        })
    )

    profit_margin = forms.IntegerField(
        min_value=0,
        max_value=100,
        initial=35,
        widget=forms.NumberInput(attrs={
            'step': '1',
        })
    )

    quantity = forms.IntegerField(
        min_value=1,
        max_value=500,
        initial=1,
        widget=forms.NumberInput(attrs={
            'step': '1',
        })
    )

    class Meta:
        model = ProductQuote
        fields = ['product', 'discount', 'profit_margin', 'quantity']

    def __init__(self, *args, index=None, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if index is not None:
                field.widget.attrs.update({
                    "id": f"{name}-{index}",
                })
            field.widget.attrs.update({
                "name": name,
                "placeholder": f"Ingrese {name}",
                "class": "w-full pl-[4px] border-2 border-[#B6B6B6] rounded-xs bg-white"
            })



class PricingForm(forms.ModelForm):
    unit_price = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={
            'step': '0.0001',
        })
    )

    subtotal = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={
            'step': '0.0001',
        })
    )

    class Meta:
        model = ProductQuote
        fields = ['unit_price', 'subtotal']

    def __init__(self, *args, index=None, custom=False, **kwargs):
        super().__init__(*args, **kwargs)
        if index is not None:
            for name, field in self.fields.items():
                field.widget.attrs.update({
                    "id": f"{name}-{index}",
                    "name": name,
                    "readonly": "readonly",
                    "class": "w-full text-right outline-none border-transparent shadow-none"
                })
            if custom:
                self.fields["subtotal"].widget.attrs.pop("readonly", None)
                self.fields["subtotal"].widget.attrs.update({
                    "class": "w-full text-right border-2 border-[#B6B6B6] rounded-xs bg-white"
                })


class ProductQuoteFullForm(forms.ModelForm):
    product = ProductQuoteForm.base_fields['product']
    discount = ProductQuoteForm.base_fields['discount']
    profit_margin = ProductQuoteForm.base_fields['profit_margin']
    quantity = ProductQuoteForm.base_fields['quantity']
    unit_price = PricingForm.base_fields['unit_price']
    subtotal = PricingForm.base_fields['subtotal']

    class Meta:
        model = ProductQuote
        fields = [
            'quote', 'product', 'discount', 'profit_margin',
            'quantity', 'unit_price', 'subtotal'
        ]

    def __init__(self, *args, index=None, **kwargs):
        super().__init__(*args, **kwargs)
        if index is not None:
            for name in self.fields:
                self.fields[name].widget.attrs.update({
                    "id": f"{name}-{index}",
                    "name": name,
                })
