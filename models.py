# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

from django.contrib.auth.models import User

from tag.models import *


# Create your models here.

class Account(models.Model):
    name = models.CharField(max_length=50, db_index=True, null=False)
    email = models.EmailField(null=True)
    password = models.CharField(max_length=255, null=True)
    cookies = models.TextField(null=True)
    tag = models.ForeignKey(Tag, related_name="account_tag")
    enable_cookie = models.IntegerField(default=0)
    enable_review = models.IntegerField(default=0)
    createuser = models.ForeignKey(User, related_name='account_create_user')
    createtime = models.DateTimeField(auto_now_add=True)
    updateuser = models.ForeignKey(User, related_name='account_update_user', null=True)
    updatetime = models.DateTimeField(auto_now=True, null=True)
    delflag = models.IntegerField(default=0)

    def __unicode__(self):
        return self.name

    class Meta:
        db_table = "account"

