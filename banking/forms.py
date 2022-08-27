from django.conf import settings
from django import forms
from django.core.validators import RegexValidator
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.forms import UserCreationForm

from core.models import User

from .models import Account


class DepositeForm(forms.ModelForm):


    class Meta:
        model = Account
        fields = ( 'balance', )

class ActiveAccountForm(forms.Form):
    phone = forms.CharField(validators=[
        RegexValidator(
            regex=r'^01?\d{9}$',
            message="Phone number must be entered in the format: '01XXXNNNNNN' in 11 digits."
        ),
    ], max_length=15, required=False
    )
    pin = forms.IntegerField(required=True, validators=[MinValueValidator(10000), MaxValueValidator(99999)])
    
    def clean(self):
        phone = self.cleaned_data['phone']
        if phone and User.objects.filter(phone=phone).exists():
            raise forms.ValidationError('Phone Number is already in use.')
        return phone


class PhoneFieldForm(forms.Form):
    phone = forms.CharField(validators=[
        RegexValidator(
            regex=r'^01?\d{9}$',
            message="Phone number must be entered in the format: '01XXXNNNNNN' in 11 digits."
        ),
    ], max_length=15, required=False
    )
        
