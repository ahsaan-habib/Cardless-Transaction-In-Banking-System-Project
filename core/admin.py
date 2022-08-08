from django.contrib import admin
from . import models

@admin.register(models.User)
class PostAdmin(admin.ModelAdmin):
    pass