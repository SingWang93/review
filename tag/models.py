# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from  django.contrib.auth.models import User


# Create your models here.



class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True, null=False)
    url = models.URLField(null=False)

    def __unicode__(self):
        return self.name

    class Meta:
        db_table = "tag"
