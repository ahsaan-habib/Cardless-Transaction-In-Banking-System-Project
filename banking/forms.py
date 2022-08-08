from django import forms
from django.core.validators import RegexValidator
from django.contrib.auth.forms import UserCreationForm

from .models import Account


class DepositeForm(forms.ModelForm):


    class Meta:
        model = Account
        fields = ( 'balance', )
        
