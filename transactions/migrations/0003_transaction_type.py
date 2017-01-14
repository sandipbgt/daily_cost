# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-01-12 08:13
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transactions', '0002_remove_transaction_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='type',
            field=models.CharField(choices=[('Income', 'Income'), ('Expense', 'Expense')], default='Expense', max_length=15),
            preserve_default=False,
        ),
    ]