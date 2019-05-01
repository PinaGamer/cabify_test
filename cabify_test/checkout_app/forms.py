from django import forms
from .models import Product


class AddItemForm(forms.Form):
    product_code = forms.ModelChoiceField(
        queryset=Product.objects.values_list('product_code', flat=True)
    )
    quantity = forms.IntegerField(min_value=1, initial=1)
