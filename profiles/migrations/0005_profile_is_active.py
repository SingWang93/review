# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2018-01-22 15:26
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0004_auto_20180115_1411'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='is_active',
            field=models.IntegerField(default=0),
        ),
    ]
