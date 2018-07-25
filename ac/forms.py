# -*- coding:utf-8 -*-
from django.forms import ModelForm
from django import forms
from models import *


class AcForm(ModelForm):
    account_CHOICES = (
        (0, u'自己的买手号'),
        (1, u'系统的买手号'),
    )
    starttime = forms.DateTimeField(widget=forms.DateInput(attrs={"class": "form-datetime am-form-field", "placeholder": u"填写中国时间"}), label="开始时间")

    class Meta:
        model = Ac
        exclude = ['id', 'createuser', 'createtime', 'updateuser', 'updatetime', 'delflag', "finish",  "sync_flag"]
