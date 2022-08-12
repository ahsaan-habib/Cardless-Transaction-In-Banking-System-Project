from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.utils import timezone
import random
from django.contrib import messages

from banking.models import Account, Transaction

@login_required(login_url='core:login')
def activate_account(request):
    user = request.user
    context = {}
    try:
        account = Account.objects.get(user=user)
        context['account_info'] = account
        if account.active:
            return redirect('core:profile')
        if request.POST:
            pin = request.POST['pin']
            context['pin'] = pin
            if pin and pin.isdigit() and int(pin) > 10000 and int(pin) < 99999 and int(pin) != account.pin:
                account.pin = int(pin)
                account.active = True
                account.save()
                messages.add_message(request, messages.INFO,
                                        'Your account has been activated. You can now make any transaction.')
                return HttpResponseRedirect(reverse('core:profile'))
            else:
                context['pin_error_message'] = "Invalid pin"
    except Account.DoesNotExist:
        context['error_message'] = "Something went wrong"
    return render(request, 'banking/activate_account.html', context)


@login_required(login_url='core:login')
def change_pin(request):
    context = {}
    if request.POST:
        current_pin = request.POST['current_pin']
        new_pin = request.POST['new_pin']
        context['current_pin'] = current_pin
        context['new_pin'] = new_pin
        if current_pin and new_pin:
            if current_pin.isdigit() and int(current_pin) > 10000 and int(current_pin) < 99999 \
and new_pin.isdigit() and int(new_pin) > 10000 and int(new_pin) < 99999 and new_pin != current_pin:
                account = Account.objects.get(user=request.user)
                if account.pin == int(current_pin):
                    account.pin = new_pin
                    account.save()
                    messages.add_message(request, messages.INFO, 'Pin changed successfully')
                    return HttpResponseRedirect(reverse('core:profile'))
                else:
                    context['pin_error_message'] = "Invalid Current pin"
            else:   
                context['pin2_error_message'] = "Invalid pin"
        else:
            context['pin2_error_message'] = "Please fill all fields"

    return render(request, 'banking/change_pin.html', context)


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
                    account = Account.objects.filter(account_no=int(account_no)).first()
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
                            messages.add_message(request, messages.INFO,
                                                    'Deposited successfully')
                        return HttpResponseRedirect(reverse('banking:deposited',  kwargs={'account_no': account_no}) )
                    else:
                        context['account_error_message'] = "Account not found"
                else:
                    context['amount_error_message'] = "Invalid amount, please enter amount \
                         between 1 and 999999999 without decimal point formate"
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
                to_account = Account.objects.filter(account_no=int(to_account_no)).first()
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
                                messages.add_message(request, messages.INFO,
                                                        'Amount transferred successfully')
                                   
                                return HttpResponseRedirect(reverse('banking:transferred',
                                kwargs={'transaction_id': created_transaction.transaction_id}) )
                                
                        else:
                            context['amount_error_message'] = "Insufficient balance"
                    else:
                        context['account_error_message'] = "You can't transfer to your own account"
                else:
                    context['account_error_message'] = "Account not found"
            else:
                context['amount_error_message'] = "Invalid amount, please enter amount \
                         between 1 and 999999999 without decimal point formate"
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




@login_required(login_url='core:login')
def make_cash_by_code(request):
    user = request.user
    context = {}
    account = Account.objects.get(user=user)
    if account.active:
        if request.POST:
            amount = request.POST['amount']
            context['amount'] = amount
            print(amount)
            if amount and amount.isdigit() and int(amount) > 0 and int(amount) < 999999999 and int(amount) % 500 == 0:
                try:
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
                            messages.add_message(request, messages.INFO, 
                                    'Generating PIN code for cash withdrawal is success. Please manage transaction PIN carefully')
                                

                        return HttpResponseRedirect(reverse('banking:pending_transaction',
                                    kwargs={'transaction_id': created_transaction.transaction_id}) )
                    else:
                        context['amount_error_message'] = "Insufficient balance"
                    
                except Account.DoesNotExist:
                    context['amount_error_message'] = "Account not found, Something went wrong, please Contact Admin"
            else:
                context['amount_error_message'] = "Amount must be multiple of 500 and in range between\
                     500 to 10000000 without decimal point formate"

    else:
        context['account_error_message'] = "Account is not active, you must activate your \
                account to make cash by code or withdraw"


    return render(request, 'banking/make_cash_by_code.html', context)


@login_required(login_url='core:login')
def pending_transaction(request, transaction_id):
    context = {}
    
    try:
        transaction = Transaction.objects.get(transaction_id=transaction_id)
        if transaction.from_account.user == request.user or ( request.user in \
             [ account.user for account in transaction.shared_accounts.all()]):
            if transaction.status == 'F':
                context['error_message'] = "This Transaction has been Faild."
            elif transaction.status == 'C':
                context['error_message'] = "This Transaction has been Completed."
            else:
                if request.POST:
                    shared_account_no = request.POST['account_no']
                    try:    
                        account = Account.objects.get(account_no=shared_account_no)
                        transaction.shared_accounts.add(account)
                        transaction.save()
                        pass
                    except Account.DoesNotExist:
                        context['account_error_message'] = "Beneficiary Account not found"
                
            context['transaction'] = transaction
            context['shared_accounts'] = transaction.shared_accounts.all()
        else:
            context['error_message'] = "You are not allowed to access this Transaction"
    except Transaction.DoesNotExist:
        context['error_message'] = "Transaction not found"
    return render(request, 'banking/pending_transaction.html', context)


@login_required(login_url='core:login')
def shared_transactions(request):
    user = request.user
    context = {}
    transactions = Transaction.objects.filter(shared_accounts__user=user, status='P')
    if transactions.__len__() > 0:
        context['transactions'] = transactions
    else:
        context['error_message'] = "No Shared transactions"
    return render(request, 'banking/shared_transactions.html', context)



@login_required(login_url='core:login')
def revert_cash_by_code(request, transaction_id):
    context = {}
    user = request.user
    try:
        trnx = Transaction.objects.get(transaction_id=transaction_id)
        account = Account.objects.get(user=user)
        if trnx.from_account == account:
            if trnx.status == 'F':
                context['error_message'] = "This Transaction has been Faild already."
            elif trnx.status == 'C':
                context['error_message'] = "This Transaction has been Completed already."
            else:
                if trnx.created_at > timezone.now() - timezone.timedelta(hours=24):
                    with transaction.atomic():
                        trnx.status = 'F'
                        trnx.transaction_type = 'W'
                        trnx.success = False
                        trnx.save()
                        account.balance += trnx.amount
                        account.save()

                        messages.add_message(request, messages.INFO,'Amount Reverted successfully')
                        return HttpResponseRedirect(reverse('banking:transaction_details',
                                    kwargs={'transaction_id': trnx.transaction_id}) )
                                    
                else:
                    context['error_message'] = "Transaction is expired"
                context['transaction'] = transaction
        else:
            context['error_message'] = "You are not allowed to access this Transaction"
    except Transaction.DoesNotExist:
        context['error_message'] = "Transaction not found"
    return render(request, 'banking/revert_cash_by_code.html', context)
