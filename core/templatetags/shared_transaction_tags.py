from django import template
from banking.models import Transaction

register = template.Library()


@register.filter
def shared_transactions(user):
    if user.is_authenticated:
        return Transaction.objects.filter(shared_accounts__in=[user.account], status="P").count()
    return 0

@register.filter
def amount_without_decimal(value):
    return str(value).split('.')[0]