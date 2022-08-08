from django.contrib import admin
from . import models

@admin.register(models.User)
class CoreAdmin(admin.ModelAdmin):
    pass