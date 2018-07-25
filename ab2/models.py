# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from tag.models import Tag
from account.models import Account


# Create your models here.

class Ab2(models.Model):
    tag = models.ForeignKey(Tag, related_name="ab2_tag", null=True, verbose_name="平台")
    url = models.CharField(max_length=500, null=True, verbose_name="URL")
    asin = models.CharField(max_length=250, null=True, verbose_name="ASIN")
    total = models.IntegerField(default=0, verbose_name="次数")
    createuser = models.ForeignKey(User, related_name="ab2_create_user")
    createtime = models.DateTimeField(auto_now_add=True)
    updateuser = models.ForeignKey(User, null=True, related_name="ab2_update_user")
    updatetime = models.DateTimeField(auto_now=True)
    starttime = models.DateTimeField(null=True)
    delflag = models.IntegerField(default=0)
    finish = models.IntegerField(default=0)
    sync_flag = models.IntegerField(default=0)

    def __unicode__(self):
        return self.url

    class Meta:
        db_table = "ab2"


class Ab2_log(models.Model):
    ab2 = models.ForeignKey(Ab2, related_name="log2_ab", null=True)
    account = models.ForeignKey(Account, related_name="log_ab2_account")
    createuser = models.ForeignKey(User, related_name="log_ab2_user")
    createtime = models.DateTimeField(auto_now_add=True)
    msg = models.TextField(null=True)
    integral = models.IntegerField(default=10)
    status = models.IntegerField(default=0)  # 0:待验证  1:成功   2:失败
    option = models.IntegerField(default=0)

    def __unicode__(self):
        return self.msg

    class Meta:
        db_table = "ab2_log"
