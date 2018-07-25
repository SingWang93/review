# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render, loader, HttpResponse, redirect, HttpResponseRedirect
from forms import AcForm
from django.db import connection, transaction
from datetime import datetime
import json
from models import *
from profiles.models import *

from review.views import ChangeForm


# Create your views here.
def index(request):
    if request.user.is_authenticated():
        if request.user.user_profile.is_active:
            forms = AcForm()
            pwd_forms = ChangeForm()
            template = loader.get_template('ac.html')
            context = {"ac": "active", "forms": forms, "pwd_forms": pwd_forms, "username": request.user.username}
            return HttpResponse(template.render(context, request))
        else:
            return HttpResponseRedirect('/notice/')
    else:
        return HttpResponseRedirect('/login/')


def tutorial(request):
    if request.user.is_authenticated():
        if request.user.user_profile.is_active:
            pwd_forms = ChangeForm()
            template = loader.get_template('tutorial/review.html')
            context = {"course_task": "active", "pwd_forms": pwd_forms, "username": request.user.username}
            return HttpResponse(template.render(context, request))
        else:
            return HttpResponseRedirect('/notice/')
    else:
        return HttpResponseRedirect('/login/')


def source(request):
    result = {}
    iDisplayStart = int(request.GET.get('iDisplayStart', 1))
    iDisplayLength = int(request.GET.get('iDisplayLength', 20))
    keyword = request.GET.get('keyword', '')
    sql = 'select a.id,a.asin,a.total,b.name as tag_name,a.createtime,a.starttime,a.sync_flag,CASE  WHEN a.sync_flag = 0 THEN "未分配"  ELSE "已分配" END AS sync_status from ac a left join tag b on a.tag_id = b.id where a.delflag=0 and a.createuser_id=%s' % request.user.id
    cursor = connection.cursor()
    if keyword:
        sql = sql + ' and  a.keyword like concat("%%",%s,"%%")'
        count = cursor.execute(sql, (keyword, keyword))
    else:
        count = cursor.execute(sql)

    start = (iDisplayStart / iDisplayLength) * iDisplayLength
    sql += ' limit %s,%s'
    if keyword:
        count = cursor.execute(sql, (keyword, keyword, start, iDisplayLength))
    else:
        cursor.execute(sql, (start, iDisplayLength))
    results = cursor.fetchall()
    columns = [column[0] for column in cursor.description]
    datas = []
    for row in results:
        datas.append(dict(zip(columns, row)))

    items = []
    for data in datas:
        for k, v in data.iteritems():
            if isinstance(v, datetime):
                data[k] = v.strftime('%Y-%m-%d %H:%M:%S')
        items.append(data)
    result['aaData'] = items
    result['iTotalRecords'] = count
    result["iTotalDisplayRecords"] = count
    return HttpResponse(json.dumps(result), content_type="application/json")


def save(request):
    obj = None
    sid = request.POST.get('id')
    try:
        if sid:
            obj = Ac.objects.get(id=sid)
            if obj.sync_flag == 1:
                result = {"ret": 10000, "status": "failed", "msg": "任务已分配,无法进行修改!"}
                return HttpResponse(json.dumps(result), content_type="application/json")
    except Ac.DoesNotExist:
        pass
    if obj:
        form = AcForm(request.POST or None, instance=obj)
    else:
        option = request.POST.get("option",0)
        total = request.POST.get('total')
        if int(option):
            accounts = Account.objects.filter(delflag=0, tag_id=request.POST.get('tag'), createuser_id=5)
            if accounts.count() == 0:
                result = {"ret": 10000, "status": "failed", "msg": "当前系统下没有买手号,请联系客服!"}
                return HttpResponse(json.dumps(result), content_type="application/json")
            integral = 150
        else:
            accounts = Account.objects.filter(delflag=0, tag_id=request.POST.get('tag'), createuser_id=request.user.id)
            if accounts.count() == 0:
                result = {"ret": 10000, "status": "failed", "msg": "当前账号下没有买手号!"}
                return HttpResponse(json.dumps(result), content_type="application/json")
            discount = request.user.user_profile.discount
            integral = int(30 * (discount / 100.0))
        total_integral = integral * int(total)
        if Profile.objects.get(user_id=request.user.id).integral < total_integral:
            result = {"ret": 10000, "status": "failed", "msg": "当前账号积分不足!"}
            return HttpResponse(json.dumps(result), content_type="application/json")
        form = AcForm(request.POST or None)
    if form.is_valid():
        instance = form.save(commit=False)
        if sid:
            instance.updateuser = request.user

        else:
            instance.createuser = request.user
        instance.save()
        result = {"ret": 0, "status": "success"}
        return HttpResponse(json.dumps(result), content_type="application/json")
    else:
        msg = []
        if form.errors:
            for k, v in form.errors.iteritems():
                msg.append(v[0])
        return HttpResponse(json.dumps({"ret": 10000, "status": "error", "msg": '\n'.join(msg)}),
                            content_type="application/json")


def delete(request):
    obj = None
    try:
        if request.POST.get('id'):
            obj = Ac.objects.get(id=request.POST.get('id'))
            if obj.sync_flag == 1:
                result = {"ret": 10000, "status": "failed", "msg": "任务已分配,无法进行删除!"}
                return HttpResponse(json.dumps(result), content_type="application/json")
    except Ac.DoesNotExist:
        pass
    if obj:
        try:
            obj.delflag = 1
            obj.save()
            result = {"ret": 0, "status": "success"}
            return HttpResponse(json.dumps(result), content_type="application/json")
        except:
            pass
    return HttpResponse(json.dumps({"ret": 10000, "status": "failed"}), content_type="application/json")


def log(request):
    if request.user.is_authenticated():
        if request.user.user_profile.is_active:
            pwd_forms = ChangeForm()
            sql = 'select c.asin,a.integral,a.createtime,CASE  WHEN status= 0 THEN "未检测"  ELSE "成功" END AS review_status,CASE  WHEN a.`option`= 0 THEN "自导"  ELSE "系统" END AS option_type,b.name from cart_log a left join account b on a.account_id= b.id left join cart c on a.cart_id = c.id where a.createuser_id=%s order by a.id desc' % request.user.id
            cursor = connection.cursor()
            cursor.execute(sql)
            results = cursor.fetchall()
            print connection.queries
            columns = [column[0] for column in cursor.description]
            datas = []
            for row in results:
                datas.append(dict(zip(columns, row)))

            items = []
            for data in datas:
                for k, v in data.iteritems():
                    if isinstance(v, datetime):
                        data[k] = v.strftime('%Y-%m-%d %H:%M:%S')
                items.append(data)
            template = loader.get_template('cart_log.html')
            context = {"cart_log": "active", "pwd_forms": pwd_forms, "username": request.user.username, "logs": items}
            return HttpResponse(template.render(context, request))
        else:
            return HttpResponseRedirect('/notice/')
    else:
        return HttpResponseRedirect('/login/')

