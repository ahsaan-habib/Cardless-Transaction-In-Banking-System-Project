from django.urls import path
from . import views

app_name = 'banking'

urlpatterns = [
    path('activate-account', views.activate_account, name='activate_account'),
    path('change-pin', views.change_pin, name='change_pin'),
    path('deposite', views.deposite, name='deposite'),
    path('deposited/<int:account_no>', views.deposited, name='deposited'),
    path('transfer', views.transfer, name='transfer'),
    path('transferred/<int:transaction_id>', views.transferred, name='transferred'),
    path('transactions/<int:transaction_id>', views.transaction_details, name='transaction_details'),
    path('atm', views.atm, name='atm'),
    path('make_cash-by-code', views.make_cash_by_code, name='make_cash_by_code'),
    path('pending-transactions/<int:transaction_id>', views.pending_transaction , name='pending_transaction'),
    path('shared-transactions', views.shared_transactions, name='shared_transactions'),
    path('withdraw', views.withdraw, name='withdraw'),
    path('cash-by-code', views.cash_by_code, name='cash_by_code'),
    path('revert-cash-by-code/<int:transaction_id>', views.revert_cash_by_code, name='revert_cash_by_code'),
]
