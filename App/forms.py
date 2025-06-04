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

    class Meta:
        model = Quote
        fields = ['client', 'salesRep']


class ProductQuoteForm(forms.ModelForm):
    product = forms.ModelChoiceField(
        queryset=Product.objects.all(),
        required=True,
        widget=forms.Select(attrs={
            'class': 'w-full pl-[4px] border-2 border-[#B6B6B6] rounded-xs',
            'list': 'product-list',
        })
    )

    discount = forms.IntegerField(
        min_value=0,
        max_value=100,
        initial=0,
        widget=forms.NumberInput(attrs={
            'class': 'w-full pl-[4px] border-2 border-[#B6B6B6] rounded-xs',
            'step': '1',
        })
    )

    profit_margin = forms.IntegerField(
        min_value=0,
        max_value=100,
        initial=35,
        widget=forms.NumberInput(attrs={
            'class': 'w-full pl-[4px] border-2 border-[#B6B6B6] rounded-xs',
            'step': '1',
        })
    )

    quantity = forms.IntegerField(
        min_value=1,
        max_value=500,
        initial=1,
        widget=forms.NumberInput(attrs={
            'class': 'w-full pl-[4px] border-2 border-[#B6B6B6] rounded-xs',
            'step': '1',
        })
    )

    class Meta:
        model = ProductQuote
        fields = ['product', 'discount', 'profit_margin', 'quantity']

    def __init__(self, *args, index=None, **kwargs):
        super().__init__(*args, **kwargs)
        if index is not None:
            for name, field in self.fields.items():
                field.widget.attrs.update({
                    "id": f"{name}-{index}",
                    "name": name,
                })



class PricingForm(forms.ModelForm):
    unit_price = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'w-1/2 text-center',
            'readonly': 'readonly',
        })
    )

    subtotal = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'w-1/2 text-center',
            'readonly': 'readonly',
        })
    )

    class Meta:
        model = ProductQuote
        fields = ['unit_price', 'subtotal']

    def __init__(self, *args, index=None, **kwargs):
        super().__init__(*args, **kwargs)
        if index is not None:
            for name, field in self.fields.items():
                field.widget.attrs.update({
                    "id": f"{name}-{index}",
                    "name": name,
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
