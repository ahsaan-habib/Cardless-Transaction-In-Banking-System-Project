from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.db import transaction
import random

from banking.models import Account, Transaction

from .forms import DepositeForm


@login_required(login_url='core:login')
def activate_account(request):
    user = request.user
    try:
        account = Account.objects.get(user=user)
        context = {}
        if request.POST:
            pin = request.POST['pin']
            context['pin'] = pin
            if pin and pin.isdigit() and int(pin) > 10000 and int(pin) < 99999:
                account.pin = pin
                account.active = True
                account.save()
                return HttpResponseRedirect(reverse('core:profile'))
            else:
                context['pin_error_message'] = "Invalid pin"
    except Account.DoesNotExist:
        context['error_message'] = "Something went wrong"
    return render(request, 'banking/activate_account.html', context)


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
                if amount.isdigit() and int(amount) > 0 and int(amount) < 999999999:
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


@login_required(login_url='core:login')
def transfer(request):
    user = request.user
    context = {}
    if request.POST:
        amount = request.POST['amount']
        to_account_no = request.POST['account_no']
        context['amount'] = amount
        context['account_no'] = to_account_no
        if amount and to_account_no:
            if amount.isdigit() and int(amount) > 0 and int(amount) < 999999999:
                to_account = Account.objects.filter(account_no=to_account_no).first()
                if to_account:
                    from_account = Account.objects.get(user=user)
                    if to_account != from_account:
                        if from_account.balance >= int(amount):
                            with transaction.atomic():
                                from_account.balance -= int(amount)
                                from_account.save()
                                to_account.balance += int(amount)
                                to_account.save()
                                created_transaction = Transaction.objects.create(
                                    to_account=to_account,
                                    from_account=from_account,
                                    amount=int(amount),
                                    transaction_type='T',
                                    status="C",
                                    success=True
                                )
                                
                                return HttpResponseRedirect(reverse('banking:transferred',
                                kwargs={'transaction_id': created_transaction.transaction_id}) )
                        else:
                            context['amount_error_message'] = "Insufficient balance"
                    else:
                        context['account_error_message'] = "You can't transfer to your own account"
                else:
                    context['account_error_message'] = "Account not found"
            else:
                context['amount_error_message'] = "Invalid amount"
        else:
            context['form_error_message'] = "Please fill all fields"
    return render(request, 'banking/transfer.html', context)


def transferred(request, transaction_id):
    context = {}
    transaction = Transaction.objects.filter(transaction_id=transaction_id).first()
    if transaction:
        context['transaction'] = transaction
        context['success_message'] = "Amount transferred successfully"
    else:
        context['error_message'] = "Transaction not found"
    return render(request, 'banking/transferred.html', context)


@login_required(login_url='core:login')
def transaction_details(request, transaction_id):
    context = {}
    if request.POST:
        trnxt_id = request.POST['transaction_id']
        return HttpResponseRedirect(reverse('banking:transaction_details',
                                kwargs={'transaction_id': trnxt_id}) )
    transaction = Transaction.objects.filter(transaction_id=transaction_id).first()
    if transaction:
        context['transaction'] = transaction
    else:
        context['error_message'] = "Transaction not found"
    return render(request, 'banking/transaction_details.html', context)


def atm(request):
    return render(request, 'banking/atm.html')


@login_required(login_url='core:login')
def make_cash_by_code(request):
    user = request.user
    context = {}
    if request.POST:
        amount = request.POST['amount']
        context['amount'] = amount
        print(amount)
        if amount and amount.isdigit() and int(amount) > 0 and int(amount) < 999999999:
            try:
                account = Account.objects.get(user=user)
                if account.balance >= int(amount):
                    with transaction.atomic():
                        account.balance -= int(amount)
                        account.save()
                        created_transaction = Transaction.objects.create(
                            from_account=account,
                            amount=int(amount),
                            transaction_type='T',
                            status="P",
                            pin =random.randint(00000000, 99999999),
                            success=False
                        )
                    return HttpResponseRedirect(reverse('banking:pending_transaction',
                                kwargs={'transaction_id': created_transaction.transaction_id}) )
                else:
                    context['amount_error_message'] = "Insufficient balance"
            except Account.DoesNotExist:
                context['amount_error_message'] = "Account not found, Something went wrong, please Contact Admin"
        else:
            context['amount_error_message'] = "Invalid amount"


    return render(request, 'banking/make_cash_by_code.html', context)


@login_required(login_url='core:login')
def pending_transaction(request, transaction_id):
    context = {}
    if request.POST:
        shared_account_no = request.POST['account_no']
        print(shared_account_no)
        pass
    try:
        transaction = Transaction.objects.get(transaction_id=transaction_id)
        if transaction.from_account.user == request.user:
            if transaction.status == 'F':
                context['error_message'] = "This Transaction has been Faild."
            elif transaction.status == 'C':
                context['error_message'] = "This Transaction has been Completed."
            else:
                pass
        context['transaction'] = transaction
    except Transaction.DoesNotExist:
        context['error_message'] = "Transaction not found"
    return render(request, 'banking/pending_transaction.html', context)



def widthdraw(request):
    context = {}
    if request.POST:
        account_no = request.POST['account_no']
        amount = request.POST['amount']
        context['account_no'] = account_no
        context['amount'] = amount
        if amount and account_no:
            if amount.isdigit() and int(amount) > 0 and int(amount) < 999999999:
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

    return render(request, 'banking/widthdraw.html', context)

