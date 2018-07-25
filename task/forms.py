# -*- coding:utf-8 -*-
'''
from django.forms import ModelForm
from django import forms
from models import *


class TaskForm(ModelForm):
    MODE_CHOICES = (
        (u'A', u'ASIN'),
        (u'S', u'SELLERID'),
    )
    # mode = forms.ModelChoiceField(queryset=MODE_CHOICES, label=u"模式")
    # keyword = forms.CharField(widget=forms.TextInput(attrs={"placeholder": u"关键词", "required": "required"}),
    #                           error_messages={"required": u"关键词不能为空",
    #                                           "invalid": u"输入一个有效的关键词",
    #                                           "unique": u"该关键词已存在"},
    #                           strip=True,
    #                           label=u"关键词")
    comment = forms.CharField(widget=forms.Textarea(attrs={"placeholder": u"评论以 | 符号分割, | 前面为评论的HeadLine,后面的为内容,一条评论一行."}), label=u"评论")

    class Meta:
        model = Task
        exclude = ['id', 'createuser', 'createtime', 'updateuser', 'updatetime', 'delflag']
'''
from django.forms import ModelForm
from django import forms
from models import *


class TaskForm(ModelForm):
    MODE_CHOICES = (
        (u'A', u'ASIN'),
        (u'S', u'SELLERID'),
    )
    starttime = forms.DateTimeField(widget=forms.DateInput(attrs={"class": "form-datetime am-form-field", "placeholder": u"填写中国时间"}), label="开始时间")
    comment = forms.CharField(widget=forms.Textarea(attrs={"placeholder": u"评论以 | 符号分割, | 前面为评论的HeadLine,后面的为内容,一条评论一行.注: | 符号必须为英文符号"}), label=u"评论")

    class Meta:
        model = Task
        exclude = ['id', 'createuser', 'createtime', 'updateuser', 'updatetime', 'delflag', "finish","review_flag","sync_flag","sync_review", "start", "end"]

