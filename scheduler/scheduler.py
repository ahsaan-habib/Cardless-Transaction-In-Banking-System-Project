from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore, register_events
from django.utils import timezone
from django_apscheduler.models import DjangoJobExecution
import sys
from banking.models import Transaction, Account
from django.db import transaction


# This is the function you want to schedule 
# - add as many as you want and then register them in the start() function below
def revert_transactions():

    transactions = Transaction.objects.filter(status='P')

    for trnx in transactions:
        if trnx.created_at < timezone.now() - timezone.timedelta(hours=24):
            with transaction.atomic():
                trnx.status = 'F'
                trnx.transaction_type = 'W'
                trnx.save()
                from_account = Account.objects.get(account_no=trnx.from_account.account_no)
                from_account.balance += trnx.amount
                from_account.save()
                print(f"Transaction {trnx.transaction_id} reverted", file=sys.stdout)
                print(f"To account {from_account.account_no} balance {from_account.balance}", file=sys.stdout)


def revert_failed_creation_of_cbc():
    transactions = Transaction.objects.filter(status='I')

    for trnx in transactions:
        if trnx.created_at < timezone.now() - timezone.timedelta(hours=1):
            with transaction.atomic():
                trnx.status = 'F'
                trnx.transaction_type = 'W'
                trnx.save()
                from_account = Account.objects.get(account_no=trnx.from_account.account_no)
                from_account.balance += trnx.amount
                from_account.save()
                print(f"Transaction {trnx.transaction_id} reverted", file=sys.stdout)
                print(f"To account {from_account.account_no} balance {from_account.balance}", file=sys.stdout)


def start():
    scheduler = BackgroundScheduler()
    scheduler.add_jobstore(DjangoJobStore(), "default")
    # run this job in every hour
    scheduler.add_job(revert_transactions, 'interval', minutes=1, name='revert_transactions', jobstore='default')
    scheduler.add_job(revert_failed_creation_of_cbc, 'interval', minutes=1, name='revert_failed_creation_of_cbc', jobstore='default')
    
    register_events(scheduler)
    scheduler.start()
    print("Scheduler started...", file=sys.stdout)