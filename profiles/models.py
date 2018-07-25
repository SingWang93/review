# -*- coding: utf-8 -*-
'''
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class Roles(models.Model):
    name = models.CharField(max_length=30, null=False, unique=True)
    provider = models.IntegerField(default=5)
    normal = models.IntegerField(default=10)
    cooperater = models.IntegerField(default=10)

    class Meta:
        db_table = "roles"



class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="user_profile")
    key = models.CharField(max_length=30, blank=True)
    iv = models.CharField(max_length=30, blank=True)
    token = models.CharField(max_length=50, blank=True)
    integral = models.IntegerField(default=0)
    discount = models.IntegerField(default=100)
    role = models.ForeignKey(Roles, related_name="profile_role", null=True)
    is_active = models.IntegerField(default=0)

    class Meta:
        db_table = "profile"

'''
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User


# Create your models here.

class Modules(models.Model):
    name = models.CharField(max_length=50, null=False, unique=True)

    def __unicode__(self):
        return self.name

    class Meta:
        db_table = "modules"


class Roles(models.Model):
    name = models.CharField(max_length=30, null=False, unique=True)

    def __unicode__(self):
        return self.name

    class Meta:
        db_table = "roles"


class cost(models.Model):
    role = models.ForeignKey(Roles, related_name="role_cost_role", null=True)
    module = models.ForeignKey(Modules, related_name="role_cost_function", null=True)
    integral = models.IntegerField(default=0)

    class Meta:
        db_table = "cost"


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="user_profile")
    key = models.CharField(max_length=30, blank=True)
    iv = models.CharField(max_length=30, blank=True)
    token = models.CharField(max_length=50, blank=True)
    integral = models.IntegerField(default=0)
    discount = models.IntegerField(default=100)
    review = models.ForeignKey(Roles, related_name="review_role", null=True,default=3)
    cart = models.ForeignKey(Roles, related_name="cart_role", null=True,default=3)
    is_active = models.IntegerField(default=0)

    class Meta:
        db_table = "profile"

