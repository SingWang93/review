# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2018-04-25 20:01
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('akh', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='akh',
            name='sellerid',
        ),
        migrations.AddField(
            model_name='akh',
            name='asin',
            field=models.CharField(max_length=250, null=True, verbose_name='Asin'),
        ),
    ]
