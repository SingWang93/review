# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2018-01-12 14:22
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('tag', '0001_initial'),
        ('account', '0001_initial'),
        ('task', '0004_auto_20180111_0817'),
    ]

    operations = [
        migrations.CreateModel(
            name='Task_log',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('createtime', models.DateTimeField(auto_now_add=True)),
                ('msg', models.TextField(null=True)),
                ('integral', models.IntegerField(default=10)),
                ('status', models.IntegerField(default=0)),
                ('account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='log_account', to='account.Account')),
                ('createuser', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='log_task_user', to=settings.AUTH_USER_MODEL)),
                ('tag', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='log_task', to='tag.Tag')),
            ],
            options={
                'db_table': 'task_log',
            },
        ),
    ]
