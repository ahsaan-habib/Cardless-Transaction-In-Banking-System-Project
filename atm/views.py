from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.db import transaction
from django.utils import timezone
from django.contrib import messages

from banking.models import Account, Transaction

def atm(request):
    return render(request, 'atm/atm.html')


# both owner and beneficiary can withdraw money with thier phone number otp
# with transaction_lock() will be needed here
def cash_by_code(request):
    context = {}
    if request.POST:
        transaction_id = request.POST['transaction_id']
        pin = request.POST['pin'] #doesn't need pin
        # add phone 
        amount = request.POST['amount']
        context['transaction_id'] = transaction_id
        context['pin'] = pin
        context['amount'] = amount  
        if transaction_id and pin and amount:
            try:
                trnx = Transaction.objects.get(transaction_id=transaction_id)
                # check if transaction created_at time greater than current time minus 24 hours
                if trnx.created_at > timezone.now() - timezone.timedelta(hours=24):
                    if trnx.pin == int(pin) and trnx.status == 'P'\
                        and int(str(trnx.amount).split('.')[0]) == int(amount):
                    
                        with transaction.atomic():
                            trnx.status = 'C'
                            trnx.transaction_type = 'W'
                            trnx.success = True
                            trnx.save()
                            messages.add_message(request, messages.INFO,'Amount Withdrawn successfully')
                            return HttpResponseRedirect(reverse('atm:atm'))
                            
                    else:
                        context['error_message'] = "Not Valid Combination To Withdraw Via Cash By Code"
                else:
                    context['error_message'] = "Transaction is expired"
            except Transaction.DoesNotExist:
                context['error_message'] = "Not Valid Combination To Withdraw Via Cash By Code"
        else:
            context['error_message'] = "Please fill all Options"
        
    return render(request, 'atm/cash_by_code.html', context)



def withdraw(request):
    context = {}
    if request.POST:
        account_no = request.POST['account_no']
        pin = request.POST['pin']
        amount = request.POST['amount']
        context['account_no'] = account_no
        context['amount'] = amount 
        context['pin'] = pin 
        if amount and account_no and pin:
            # amount must be divided by 500 to get the number of notes
            if amount.isdigit() and int(amount) > 0 and int(amount) < 999999999 and int(amount) % 500 == 0:
            
                if pin.isdigit() and int(pin) > 10000 and int(pin) < 99999:
                    try:
                        account = Account.objects.get(account_no=int(account_no))
                        if account.active:
                            if account.balance >= int(amount):
                                if account.pin == int(pin):
                                    with transaction.atomic():
                                        account.balance -= int(amount)
                                        Transaction.objects.create(
                                            from_account=account,
                                            amount=int(amount),
                                            transaction_type='W',
                                            status="C",
                                            success=True
                                        )
                                        account.save()
                                        messages.add_message(request, messages.INFO, 
                                        'Withdrawal Successful, Thanks for using our services')
                                    return HttpResponseRedirect(reverse('atm:atm') )
                                else:
                                    context['error_message'] = "Invalid pin"
                            else:
                                context['error_message'] = "Insufficient balance"
                        else:
                            context['error_message'] = "Account is not active"
                    except Account.DoesNotExist:
                        context['error_message'] = "Account not found"
                else:
                    context['error_message'] = "Invalid pin"
            else:
                context['error_message'] = "Amount must be multiple of 500 and in range between 500 to 10000000"
        else:
            context['error_message'] = "Please fill all Options"

    return render(request, 'atm/withdraw.html', context)
