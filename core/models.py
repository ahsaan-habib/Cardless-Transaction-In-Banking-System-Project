from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.db import models
import uuid

from core.custom_auth.usermanager import MyUserManager
from core.validators import validate_file_size

class User(AbstractBaseUser, PermissionsMixin):

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    username = models.CharField(max_length=30, unique=True, null=True, blank=True)
    email = models.EmailField(verbose_name="email", max_length=64, null=True, blank=True)
    phone = models.CharField(validators=[
        RegexValidator(
            regex=r'^01?\d{9}$',
            message="Phone number must be entered in the format: '01XXXNNNNNN' in 11 digits."
        ),
    ], verbose_name="mobile number", max_length=15, unique=False, null=True, blank=True
    )

    date_joined = models.DateTimeField(verbose_name='date joined', auto_now_add=True)
    last_login = models.DateTimeField(verbose_name='last login', auto_now=True, null=True)
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    user_type_choices = (
        ('A', 'Admin'),
        ('E', 'Employee'),
        ('C', 'Customer'),
    )
    user_type = models.CharField(max_length=1, choices=user_type_choices, default='C')

    first_name = models.CharField(max_length=64, blank=True)
    last_name = models.CharField(max_length=64, blank=True)

    image = models.ImageField(
        upload_to='core/images/profile_images/',
        validators=[validate_file_size],
        blank=True, null=True)


    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    objects = MyUserManager()

    def __str__(self):
        if self.username:
            return f"username: {self.username}"
        elif not self.email:
            return f"phone: {self.phone}"
        return f"email: {self.email}"

    # For checking permissions. to keep it simple all admin have ALL permissions
    def has_perm(self, perm, obj=None):
        return self.is_admin

    # Does this user have permission to view this app? (ALWAYS YES FOR SIMPLICITY)
    def has_module_perms(self, app_label):
        return True

    def save(self, *args, **kwargs):
        if not self.email and not self.phone:
            raise ValidationError('At least one of email or phone must be provided')

        if self.email and self.__class__._default_manager.exclude(pk=self.pk).filter(email=self.email).count() > 0:
            raise ValidationError('Email is already in use.')
        
        if self.phone and self.__class__._default_manager.exclude(pk=self.pk).filter(phone=self.phone).count() > 0:
            raise ValidationError('Phone Number is already in use.')

        return super(User, self).save(*args, **kwargs)



   