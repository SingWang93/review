# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from tag.models import Tag
from account.models import Account


# Create your models here.

class Akh(models.Model):
    tag = models.ForeignKey(Tag, related_name="akh_tag", null=True, verbose_name="平台")
    keyword = models.CharField(max_length=250, null=True, verbose_name="关键词")
    asin = models.CharField(max_length=250, null=True, verbose_name="Asin")
    total = models.IntegerField(default=0, verbose_name="次数")
    createuser = models.ForeignKey(User, related_name="akh_create_user")
    createtime = models.DateTimeField(auto_now_add=True)
    updateuser = models.ForeignKey(User, null=True, related_name="akh_update_user")
    updatetime = models.DateTimeField(auto_now=True)
    starttime = models.DateTimeField(null=True)
    delflag = models.IntegerField(default=0)
    finish = models.IntegerField(default=0)
    sync_flag = models.IntegerField(default=0)

    def __unicode__(self):
        return self.asin

    class Meta:
        db_table = "akh"


class Akh_log(models.Model):
    akh = models.ForeignKey(Akh, related_name="log_akh", null=True)
    account = models.ForeignKey(Account, related_name="log_akh_account")
    createuser = models.ForeignKey(User, related_name="log_akh_user")
    createtime = models.DateTimeField(auto_now_add=True)
    msg = models.TextField(null=True)
    integral = models.IntegerField(default=10)
    status = models.IntegerField(default=0)  # 0:待验证  1:成功   2:失败
    option = models.IntegerField(default=0)

    def __unicode__(self):
        return self.msg

    class Meta:
        db_table = "akh_log"
