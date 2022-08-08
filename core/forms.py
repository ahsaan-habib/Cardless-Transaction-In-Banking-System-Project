from django import forms
from django.core.validators import RegexValidator
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _

from .models import User


class RegistrationForm(UserCreationForm):
    phone = forms.CharField(max_length=24, required=False)

    class Meta:
        model = User
        fields = ('email', 'phone', 'password1', 'password2', )
        

        help_texts = {
                'email': _("You must provide a valid email address, Don't have any email? choose phone number option instead."),
                'phone': _("Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."),
            }
    
    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control form-control-sm'
        

    def clean(self):
        email = self.cleaned_data['email']
        phone = self.cleaned_data['phone']
        if not email and not phone:
            raise forms.ValidationError('At least one of email or phone must be provided')
        
        if email and User.objects.exclude(pk=self.instance.pk).filter(email=email).count() > 0:
                raise forms.ValidationError('Email is already in use.')
        
        if phone and User.objects.exclude(pk=self.instance.pk).filter(phone=phone).count() > 0:
                raise forms.ValidationError('Phone Number is already in use.')
            
        return self.cleaned_data

   



class AuthenticateForm(forms.ModelForm):
    email_or_phone = forms.CharField(label="Email or Phone Number", max_length=64, help_text="Enter your email or phone number")
    password = forms.CharField(label='Password', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('email_or_phone', 'password')

    def __init__(self, *args, **kwargs):
        super(AuthenticateForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control form-control-sm'

    def clean(self):
        if self.is_valid():
            email_or_phone = self.cleaned_data['email_or_phone']
            password = self.cleaned_data['password']
            if not authenticate(email_or_phone=email_or_phone, password=password):
                raise forms.ValidationError('Invalid Email Or Password')


class ProfileImageUpdateForm(forms.ModelForm):
    image = forms.ImageField(label="Profile Picture", required=False)

    class Meta:
        model = User
        fields = ('image',)


class ProfileUpdateForm(forms.ModelForm):
    email = forms.EmailField(label="Email", required=False)
    phone = forms.CharField(validators=[
                                RegexValidator(
                                    regex=r'^\+?1?\d{9,15}$',
                                    message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
                                    ),
                                ], required=False
                            ) 
    
    class Meta:
        model = User
        fields = ('first_name', 'last_name','email', 'phone', 'username', )

    def __init__(self, *args, **kwargs):
        super(ProfileUpdateForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control form-control-sm rounded-0'

    def clean_email(self):
        email = self.cleaned_data['email']
        if email and User.objects.exclude(pk=self.instance.pk).filter(email=email).exists():
            raise forms.ValidationError('Email is already in use.')
        return email
    
    def clean_phone(self):
        phone = self.cleaned_data['phone']
        if phone and User.objects.exclude(pk=self.instance.pk).filter(phone=phone).exists():
            raise forms.ValidationError('Phone Number is already in use.')
        return phone

    def clean_username(self):
        username = self.cleaned_data['username']
        if username and User.objects.exclude(pk=self.instance.pk).filter(username=username).exists():
            raise forms.ValidationError('Username is already in use.')
        return username
