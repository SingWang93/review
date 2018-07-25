# -*- coding: utf-8 -*-
'''
from __future__ import unicode_literals

from django.db import models
from  django.contrib.auth.models import User
from tag.models import Tag


# Create your models here.

class Task(models.Model):
    MODE_CHOICES = (
        (u'A', u'ASIN'),
        (u'S', u'SELLERID'),
    )
    tag = models.ForeignKey(Tag, related_name="task_tag", null=True,verbose_name="平台")
    mode = models.CharField(max_length=2, choices=MODE_CHOICES,default="A",verbose_name="类型")
    keyword = models.CharField(max_length=250, null=False,verbose_name="关键词")
    total = models.IntegerField(default=0,verbose_name="评论总数")
    comment = models.TextField(null=False,verbose_name="评论")
    createuser = models.ForeignKey(User, related_name="rank_create_user")
    createtime = models.DateTimeField(auto_now_add=True)
    updateuser = models.ForeignKey(User, null=True, related_name="rank_update_user")
    updatetime = models.DateTimeField(auto_now=True)
    delflag = models.IntegerField(default=0)

    def __unicode__(self):
        return self.keyword

    class Meta:
        db_table = "task"

'''
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from tag.models import Tag
from account.models import Account

# Create your models here.

class Task(models.Model):
    MODE_CHOICES = (
        (u'A', u'ASIN'),
        (u'S', u'SELLERID'),
    )
    ACCOUNT_CHOICES = (
        (0, u'自导买手号'),
        (1, u'系统买手号 -- 100积分/次'),
    )
    Name_CHOICES = (
        (0, u'默认姓名'),
        (1, u'男名'),
        (2, u'女名'),
        (3, u'匿名'),
    )

    tag = models.ForeignKey(Tag, related_name="task_tag", null=True, verbose_name="平台")
    mode = models.CharField(max_length=2, choices=MODE_CHOICES, default="A", verbose_name="类型")
    option = models.IntegerField(choices=ACCOUNT_CHOICES, default="0", verbose_name="账号类型")
    keyword = models.CharField(max_length=250, null=False, verbose_name="Asin")
    total = models.IntegerField(default=0, verbose_name="评论总数")
    comment = models.TextField(null=False, verbose_name="评论")
    createuser = models.ForeignKey(User, related_name="rank_create_user")
    createtime = models.DateTimeField(auto_now_add=True)
    updateuser = models.ForeignKey(User, null=True, related_name="rank_update_user")
    updatetime = models.DateTimeField(auto_now=True)
    starttime = models.DateTimeField(null=True)
    delflag = models.IntegerField(default=0)
    finish = models.IntegerField(default=0)
    review_flag = models.IntegerField(default=0)
    start = models.IntegerField(default=5)
    end = models.IntegerField(default=10)
    name_type = models.IntegerField(choices=Name_CHOICES, default="0", verbose_name="留评姓名")
    sync_flag = models.IntegerField(default=0)
    sync_review = models.IntegerField(default=0)

    def __unicode__(self):
        return self.keyword

    class Meta:
        db_table = "task"

class Task_log(models.Model):
    tid = models.IntegerField(null=True)
    task = models.ForeignKey(Task, related_name="log_task",null=True, db_index=True)
    asin = models.CharField(max_length=50,null=True)
    content = models.TextField(null=True)
    account = models.ForeignKey(Account, related_name="log_account")
    createuser = models.ForeignKey(User, related_name="log_task_user", db_index=True)
    createtime = models.DateTimeField(auto_now_add=True)
    msg = models.TextField(null=True)
    integral = models.IntegerField(default=10)
    reviewid =  models.CharField(max_length=50,null=True)
    status = models.IntegerField(default=0)  # 0:待验证  1:成功   2:失败

    def __unicode__(self):
        return self.msg

    class Meta:
        db_table = "task_log"
