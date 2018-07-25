# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from tag.models import Tag
from account.models import Account


# Create your models here.

class Ass(models.Model):
    ACCOUNT_CHOICES = (
        (0, u'自导买手号'),
        (1, u'系统买手号 -- 50积分/次'),
    )

    WISH_CHOICES = (
        (0, u'否'),
        (1, u'是'),
    )

    tag = models.ForeignKey(Tag, related_name="ass_tag", null=True, verbose_name="平台")
    keyword = models.CharField(max_length=250, null=True, verbose_name="关键词")
    asin =  models.CharField(max_length=250, null=True, verbose_name="ASIN")
    sellerid = models.CharField(max_length=250, null=True, verbose_name="SellerId")
    total = models.IntegerField(default=0, verbose_name="次数")
    createuser = models.ForeignKey(User, related_name="ass_create_user")
    createtime = models.DateTimeField(auto_now_add=True)
    updateuser = models.ForeignKey(User, null=True, related_name="ass_update_user")
    updatetime = models.DateTimeField(auto_now=True)
    starttime = models.DateTimeField(null=True)
    delflag = models.IntegerField(default=0)
    finish = models.IntegerField(default=0)
    sync_flag = models.IntegerField(default=0)

    def __unicode__(self):
        return self.asin

    class Meta:
        db_table = "ass"


class Ass_log(models.Model):
    ass = models.ForeignKey(Ass, related_name="log_ass", null=True)
    account = models.ForeignKey(Account, related_name="log_ass_account")
    createuser = models.ForeignKey(User, related_name="log_ass_user")
    createtime = models.DateTimeField(auto_now_add=True)
    msg = models.TextField(null=True)
    integral = models.IntegerField(default=10)
    status = models.IntegerField(default=0)  # 0:待验证  1:成功   2:失败
    option = models.IntegerField(default=0)

    def __unicode__(self):
        return self.msg

    class Meta:
        db_table = "ass_log"
