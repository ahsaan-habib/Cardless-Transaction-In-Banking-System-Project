from django.urls import path
from . import views

app_name = 'banking'

urlpatterns = [
    path('deposite', views.deposite, name='deposite'),
    path('deposited/<int:account_no>', views.deposited, name='deposited'),
    path('transfer', views.transfer, name='transfer'),
    path('transferred/<int:transaction_id>', views.transferred, name='transferred'),
    path('transactions/<int:transaction_id>', views.transaction_details, name='transaction_details'),
]
