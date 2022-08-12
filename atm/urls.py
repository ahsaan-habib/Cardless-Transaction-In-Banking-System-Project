from django.urls import path
from . import views

app_name = 'atm'

urlpatterns = [
    path('atm', views.atm, name='atm'),
    path('withdraw', views.withdraw, name='withdraw'),
    path('cash-by-code', views.cash_by_code, name='cash_by_code'),
]

