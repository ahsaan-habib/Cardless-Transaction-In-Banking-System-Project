import uuid
from django.conf import settings
from django.db import models

class Account(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    account_no = models.CharField(max_length=10)
    balance = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    

    def __str__(self):
        return f"{self.account_no} - {self.balance}"


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
    transaction_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
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
