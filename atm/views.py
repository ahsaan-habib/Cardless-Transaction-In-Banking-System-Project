from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.db import transaction
from django.utils import timezone
from django.contrib import messages
from atm.form import CBCTransactionForm
import random

from banking.models import Account, Transaction
from core.models import User

def atm(request):
    return render(request, 'atm/atm.html')


# both owner and beneficiary can withdraw money with thier phone number otp
# with transaction_lock() will be needed here
def cash_by_code(request):
    context = {}
    if request.POST:
        try:
            amount = int(request.POST.get('amount'))
            context['amount'] = amount
            context['transaction_id'] = request.POST.get('transaction_id')
            context['phone'] = request.POST.get('cbc_beneficiary_phone')
            form = CBCTransactionForm(request.POST or None)
            if form.is_valid():
                transaction_id = form.cleaned_data.get('transaction_id')
                phone = form.cleaned_data.get('cbc_beneficiary_phone')
                if transaction_id and amount and phone:
                    try:
                        trnx = Transaction.objects.get(transaction_id=transaction_id)
                        # check if transaction created_at time greater than current time minus 24 hours
                        if trnx.created_at > timezone.now() - timezone.timedelta(hours=24):
                            # check if user input is valid
                            if trnx.status == 'P' and int(str(trnx.amount).split('.')[0]) == amount:
                                
                                if trnx.from_account.user.phone == phone:
                                        return HttpResponseRedirect(reverse('atm:verify_cbc_otp', kwargs={'transaction_id': transaction_id, 'phone': phone}) )
                                    
                                elif trnx.cbc_beneficiary_account and trnx.cbc_beneficiary_account.user.phone == phone:
                                        return HttpResponseRedirect(reverse('atm:verify_cbc_otp', kwargs={'transaction_id': transaction_id, 'phone': phone}) )
                                    
                                elif trnx.cbc_beneficiary_phone and trnx.cbc_beneficiary_phone == phone:
                                        return HttpResponseRedirect(reverse('atm:verify_cbc_otp', kwargs={'transaction_id': transaction_id, 'phone': phone}) )
                                else:
                                    context['error_message'] = "Phone Number is not valid, Please Ensure Beneficiary has Active Phone associated with account"
                            else:
                                context['error_message'] = "Not Valid Combination To Withdraw Via Cash By Code"
                        else:
                            context['error_message'] = "Transaction is expired"
                    except Transaction.DoesNotExist:
                        context['error_message'] = "Not Valid Combination To Withdraw Via Cash By Code"

                else:
                    context['error_message'] = "Please fill all Options"
            else:
                context['form'] = form
        except TypeError:
            context['error_message'] = "Not Valid Combination To Withdraw Via Cash By Code"
        
    return render(request, 'atm/cash_by_code.html', context)



def withdraw_by_verifying_otp(request, transaction_id, phone):
    try:
        check_trnx = Transaction.objects.get(transaction_id=transaction_id, status='P')
    
        if str(check_trnx.from_account.user.phone) == phone:
            pass
        elif check_trnx.cbc_beneficiary_account and str(check_trnx.cbc_beneficiary_account.user.phone) == phone:
            pass
        elif check_trnx.cbc_beneficiary_phone and str(check_trnx.cbc_beneficiary_phone) == phone:
            pass
        else:
            messages.add_message(request, messages.ERROR, "Phone Number not valid or something went wrong!")
            return HttpResponseRedirect(reverse('atm:atm'))
        
        if request.POST:
            otp = request.POST.get('otp')
            print(int(phone))
            try:
                trnx = Transaction.objects.select_for_update().get(transaction_id=transaction_id, status='P')
                try:
                    if trnx.otp == int(otp):
                        with transaction.atomic():
                            trnx.status = 'C'
                            trnx.transaction_type = 'W'
                            trnx.success = True
                            trnx.cbc_beneficiary_phone=phone
                            trnx.save()
                            messages.add_message(request, messages.INFO, 
                                'Cash By Code Transaction Succesfully Completed!')
                    else:
                        messages.add_message(request, messages.INFO, "Invalid OTP Provided.")
                except TypeError:
                    messages.add_message(request, messages.INFO, "Invalid OTP Provided.")
            except Transaction.DoesNotExist:
                messages.add_message(request, messages.ERROR, "Transaction Expired Or Locked, Please Contact Support If This Problem Persist.")
            return HttpResponseRedirect(reverse('atm:atm'))
        else:
            # send OTP via SMS to the phone number
            otp = random.randint(100000, 999999)
            check_trnx.otp = otp
            check_trnx.save()
            text = f"TheDear Customer, Your One-Time Password is {otp}. Please use this OTP to complete the transaction within 150 seconds."
            from sms import send_sms
            send_sms(
                text,
                '+8801568267336',
                [phone],
                fail_silently=False
            )
        return render(request, 'atm/verify_cbc_otp.html', {})
    except Transaction.DoesNotExist:
        messages.add_message(request, messages.ERROR, "Transaction Not Valid at this moment")
        return HttpResponseRedirect(reverse('atm:atm'))
                                



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
            if amount.isdigit() and int(amount) > 0 and int(amount) <= 1000000 and int(amount) % 500 == 0:
            
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
                context['error_message'] = "Amount must be multiple of 500 and in range between 500 to 100000"
        else:
            context['error_message'] = "Please fill all Options"

    return render(request, 'atm/withdraw.html', context)
