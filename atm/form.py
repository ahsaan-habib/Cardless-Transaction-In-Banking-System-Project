from django.conf import settings
from django import forms
from django.core.validators import RegexValidator
from django.core.validators import MinValueValidator, MaxValueValidator

from core.models import User

from banking.models import Transaction

class CBCTransactionForm(forms.Form):
    transaction_id = forms.CharField( max_length=24, required=True)
    cbc_beneficiary_phone = forms.CharField(validators=[
        RegexValidator(
            regex=r'^01?\d{9}$',
            message="Phone number must be entered in the format: '01XXXNNNNNN' in 11 digits."
        ),
    ], max_length=15, required=True
    )

    class Meta:
        model = Transaction
        fields = ( 'transaction_id', 'cbc_beneficiary_phone')

