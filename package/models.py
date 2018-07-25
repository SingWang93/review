# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User


# Create your models here.


class Package(models.Model):
    name = models.CharField(max_length=50, null=False, unique=True)
    price = models.IntegerField(default=1000)
    integral = models.IntegerField(default=10000)
    display = models.IntegerField(default=1)

    def __unicode__(self):
        return self.name

    class Meta:
        db_table = "package"


class Order(models.Model):
    order_id = models.IntegerField()
    createuser = models.ForeignKey(User, related_name="order_user")
    createtime = models.DateTimeField(auto_now_add=True)
    package = models.ForeignKey(Package, related_name="order_package")
    pay_method = models.IntegerField(default=0)  # 0: alipay   1:wechatpay
    pay_datetime = models.DateTimeField(null=True)
    status = models.IntegerField(default=0)  # 0:未付款  1:付款成功

    def __unicode__(self):
        return self.order_id

    class Meta:
        db_table = "order"


