from django.urls import path
from . import views

app_name = 'banking'

urlpatterns = [
    path('deposite', views.deposite, name='deposite'),
    path('deposited/<int:account_no>', views.deposited, name='deposited'),

]
