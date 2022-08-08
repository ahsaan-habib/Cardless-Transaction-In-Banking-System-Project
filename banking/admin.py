from django.contrib import admin
from . import models

@admin.register(models.Account)
@admin.register(models.Transaction)

class AccountAdmin(admin.ModelAdmin):
    pass