from django import forms
from .models import Client, SalesRep, Quote, Product, ProductQuote, Group


class QuoteForm(forms.ModelForm):
    public_id = forms.IntegerField(
        widget=forms.NumberInput(attrs={'type': 'hidden'})
    )

    client = forms.ModelChoiceField(
        queryset=Client.objects.all(),
        required=True,
        empty_label="Sin cliente",
        widget=forms.Select(attrs={
            'class': 'border-2 border-[#B6B6B6] rounded px-2 py-1 w-48',
            'list': 'client-list',
        })
    )

    salesRep = forms.ModelChoiceField(
        queryset=SalesRep.objects.all(),
        required=True,
        empty_label="Sin representante",
        widget=forms.Select(attrs={
            'class': 'border-2 border-[#B6B6B6] rounded px-2 py-1 w-48',
            'list': 'client-list',
        })
    )

    class Meta:
        model = Quote
        fields = ['public_id', 'client', 'salesRep']

    def __init__(self, *args, public_id=None, **kwargs):
        super().__init__(*args, **kwargs)
        if public_id is not None:
            for name, field in self.fields.items():
                field.widget.attrs.update({
                    "id": f"{name}-{public_id}",
                    "name": name,
                })



class ProductQuoteForm(forms.ModelForm):
    group = forms.ModelChoiceField(
        queryset=Group.objects.all(),
        required=False,
        empty_label="Sin grupo",
        widget=forms.Select(attrs={
            'class': 'w-full border-2 border-[#B6B6B6] rounded px-1',
            'list': 'group-list',
        })
    )

    product = forms.ModelChoiceField(
        queryset=Product.objects.all(),
        required=True,
        widget=forms.Select(attrs={
            'class': 'w-full pl-[4px] border-2 border-[#B6B6B6] rounded-sm',
            'list': 'product-list',
        })
    )

    discount = forms.IntegerField(
        min_value=0,
        max_value=100,
        initial=0,
        widget=forms.NumberInput(attrs={
            'class': 'w-full pl-[4px] border-2 border-[#B6B6B6] rounded-sm',
            'step': '1',
        })
    )

    profit_margin = forms.IntegerField(
        min_value=0,
        max_value=100,
        initial=35,
        widget=forms.NumberInput(attrs={
            'class': 'w-full pl-[4px] border-2 border-[#B6B6B6] rounded-sm',
            'step': '1',
        })
    )

    quantity = forms.IntegerField(
        min_value=1,
        max_value=500,
        initial=1,
        widget=forms.NumberInput(attrs={
            'class': 'w-full pl-[4px] border-2 border-[#B6B6B6] rounded-sm',
            'step': '1',
        })
    )

    class Meta:
        model = ProductQuote
        fields = ['group', 'product', 'discount', 'profit_margin', 'quantity']

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
    group = ProductQuoteForm.base_fields['group']
    product = ProductQuoteForm.base_fields['product']
    discount = ProductQuoteForm.base_fields['discount']
    profit_margin = ProductQuoteForm.base_fields['profit_margin']
    quantity = ProductQuoteForm.base_fields['quantity']
    unit_price = PricingForm.base_fields['unit_price']
    subtotal = PricingForm.base_fields['subtotal']

    class Meta:
        model = ProductQuote
        fields = [
            'quote', 'group', 'product', 'discount', 'profit_margin',
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
