# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2018-01-14 15:01
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0002_profile_integral'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='discount',
            field=models.IntegerField(default=100),
        ),
    ]
