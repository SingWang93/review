# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2018-01-17 07:26
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0002_account_review_flag'),
    ]

    operations = [
        migrations.AlterField(
            model_name='account',
            name='review_flag',
            field=models.IntegerField(default=1),
        ),
    ]