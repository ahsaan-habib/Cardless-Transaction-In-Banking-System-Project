# Generated by Django 4.0.4 on 2022-08-09 18:32

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('banking', '0008_alter_account_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transaction',
            name='pin',
            field=models.PositiveIntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(10000000), django.core.validators.MaxValueValidator(99999999)]),
        ),
    ]
