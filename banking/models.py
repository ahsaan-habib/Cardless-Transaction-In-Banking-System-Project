import uuid
from django.conf import settings

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import models

import random
from django.utils import timezone

def generate_pk():
    number = random.randint(00000000, 99999999)
    return '{}{}'.format(timezone.now().strftime('%Y%m%d'), number)

def generate_trnx():
    number = random.randint(0000000000, 9999999999)
    return '{}{}'.format(timezone.now().strftime('%y%m%d%H%M%S'), number)


class Account(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    account_no = models.CharField(default=generate_pk, primary_key=True, max_length=16, unique=True)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    

    def __str__(self):
        return f"{self.user} - {self.account_no}"


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        if instance and instance.user_type == 'C':
            Account.objects.create(user=instance)


class Transaction(models.Model):
    transaction_type_choices = (    
        ('T', 'Transfer'),
        ('D', 'Deposite'),
        ('W', 'Withdraw'),
    )
    transaction_status_choices = (
        ('P', 'Pending'),
        ('C', 'Complete'),
        ('R', 'Failed'),
    )
    transaction_id = models.CharField(default=generate_trnx, primary_key=True, max_length=24, unique=True)
    transaction_type = models.CharField(max_length=1, choices=transaction_type_choices, default='W')
    from_account = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True, blank=True, related_name='sender')
    to_account = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True, blank=True, related_name='reciever')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    pin = models.CharField(max_length=8, blank=True, null=True)
    status = models.CharField(max_length=1, choices=transaction_status_choices, default='P')
    success = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return f"{self.from_account} - {self.amount}"
