from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.db import transaction

from banking.models import Account, Transaction

from .forms import DepositeForm

# Create your views here.

@login_required(login_url='core:login')
def deposite(request):
    user = request.user
    context = {}
    if user.user_type == 'A' or user.user_type == 'E':
        if request.POST:
            amount = request.POST['amount']
            account_no = request.POST['account_no']
            context['amount'] = amount
            context['account_no'] = account_no
            if amount and account_no:
                if amount.isdigit() and int(amount) > 0 and int(amount) < 1000000:
                    account = Account.objects.filter(account_no=account_no).first()
                    if account:

                        with transaction.atomic():
                            account.balance += int(amount)
                            Transaction.objects.create(
                                to_account=account,
                                amount=int(amount),
                                transaction_type='D',
                                status="C",
                                success=True
                            )
                            account.save()
                        return HttpResponseRedirect(reverse('banking:deposited',  kwargs={'account_no': account_no}) )
                    else:
                        context['account_error_message'] = "Account not found"
                else:
                    context['amount_error_message'] = "Invalid amount"
            else:
                context['form_error_message'] = "Please fill all fields"
    else:
        context["unauthorized"] = "you are not allwoed to access this page"
    return render(request, 'banking/deposite.html', context)


@login_required(login_url='core:login')
def deposited(request, account_no):
    user = request.user
    context = {}
    if user.user_type == 'A' or user.user_type == 'E':
        account = Account.objects.filter(account_no=account_no).first()
        if account:
            context['account_no'] = account_no
            context['success_message'] = "Amount deposited successfully"
            context['account_info'] = account
    else:
        context["unauthorized"] = "you are not allwoed to access this page"
    return render(request, 'banking/deposited.html', context)