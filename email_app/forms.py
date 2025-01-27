from django import forms
from .models import Store, QualityResolution, Marketplace, DevEmail

class EmailGeneratorForm(forms.Form):
    CASE_TYPES = [
        ('missing', 'Missing - Store'),
        ('damaged', 'Damaged - Store'),
        ('wrong', 'Wrong - Store'),
        ('rotten', 'Rotten'),
        ('bad_smell', 'Bad Smell'),
        ('expired', 'Expired'),
        ('near_expiry', 'Near Expiry'),
        ('dev', 'Dev'),
        ('marketplace_seller', 'Marketplace - Seller'),
        ('marketplace_myl', 'Marketplace - IMILE'),
        ('marketplace_arx', 'Marketplace - ARAMEX'),
    ]

    case_type = forms.ChoiceField(choices=CASE_TYPES)
    store_name = forms.ModelChoiceField(queryset=Store.objects.all(), required=False)
    order_id = forms.CharField(max_length=255, required=False)

    # Fields for quality issues
    resolution = forms.ModelChoiceField(queryset=QualityResolution.objects.all(), required=False)
    customer_name = forms.CharField(max_length=255, required=False)
    customer_phone = forms.CharField(max_length=20, required=False)
    item_name = forms.CharField(max_length=255, required=False)
    barcode = forms.CharField(max_length=255, required=False)
    seller_email = forms.EmailField(required=False)


    # forms.py


