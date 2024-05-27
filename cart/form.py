# cart/forms.py

from django import forms


class OrderForm(forms.Form):
    table_number = forms.IntegerField(label='Table Number')
    note = forms.CharField(label='Special Instructions', widget=forms.Textarea, required=False)