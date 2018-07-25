# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models


# Create your models here.


class Integral(models.Model):
    name = models.CharField(max_length=50, null=False, unique=True)
    describe = models.TextField(null=True)
    site = models.CharField(max_length=500, null=True)
    integral = models.IntegerField(default=30)
    display = models.IntegerField(default=1)

    def __unicode__(self):
        return self.name

    class Meta:
        db_table = "integral"

