# -*- coding:utf-8 -*-
from django.forms import ModelForm
from django import forms
from models import Account


class AccountForm(ModelForm):
    name = forms.CharField(widget=forms.TextInput(attrs={"placeholder": u"名称", "required": "required"}),
                           error_messages={"required": u"名称不能为空",
                                           "invalid": u"输入一个有效的名称",
                                           "unique": u"该名称已存在"},
                           strip=True,
                           label=u"名称")
    email = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder': u'邮箱'}),
                             label=u"邮箱")
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"placeholder": u"密码", "required": "required"}),
        strip=True,
        label=u"密码")
    cookies = forms.CharField(widget=forms.Textarea(attrs={"placeholder": u"Cookies"}),
                              strip=True, required=False,
                              label=u"Cookies")

    class Meta:
        model = Account
        exclude = ['id', 'createuser', 'createtime', 'updateuser', 'updatetime', 'delflag', "enable_cookie", "enable_review","tag"]

