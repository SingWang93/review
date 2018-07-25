# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render, loader, HttpResponse, redirect, HttpResponseRedirect
from forms import TaskForm
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
            forms = TaskForm()
            pwd_forms = ChangeForm()
            template = loader.get_template('review.html')
            context = {"task": "active", "forms": forms, "pwd_forms": pwd_forms, "username": request.user.username}
            return HttpResponse(template.render(context, request))
        else:
            return HttpResponseRedirect('/notice/')
    else:
        return HttpResponseRedirect('/login/')

def index_bak(request):
    if request.user.is_authenticated():
        forms = TaskForm()
        pwd_forms = ChangeForm()
        template = loader.get_template('review.html')
        context = {"task": "active", "forms": forms, "pwd_forms": pwd_forms,"username": request.user.username}
        return HttpResponse(template.render(context, request))
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


def tutorial_bak(request):
    if request.user.is_authenticated():
        pwd_forms = ChangeForm()
        template = loader.get_template('tutorial/review.html')
        context = {"course_task": "active", "pwd_forms": pwd_forms, "username": request.user.username}
        return HttpResponse(template.render(context, request))
    else:
        return HttpResponseRedirect('/login/')



def source(request):
    result = {}
    iDisplayStart = int(request.GET.get('iDisplayStart', 1))
    iDisplayLength = int(request.GET.get('iDisplayLength', 20))
    keyword = request.GET.get('keyword', '')
#    sql = '''SELECT a.*,a.tag_id as tag,b.name as tag_name from task a left join tag b on a.tag_id = b.id where a.delflag=0 and a.createuser_id=%s''' % request.user.id
#    sql = '''SELECT a.*,a.left(a.comment,20) as comment,a.tag_id,CASE  WHEN a.sync_flag = 0 THEN "未分配"  ELSE "已分配" END AS sync_status,CASE  WHEN a.finish = 0 THEN "未完成"  ELSE "已完成" END AS review_status,b.name as tag_name from task a left join tag b on a.tag_id = b.id where a.delflag=0 and a.createuser_id=%s''' % request.user.id
    sql = '''SELECT a.id,a.tag_id as tag,a.sync_flag,CASE  WHEN a.`mode` = "A" THEN "ASIN"  ELSE "SELLERID" END AS `mode_type`,a.mode,a.total,a.createtime,a.starttime,a.keyword,CONCAT(left(a.comment,30),"...") as content,a.comment,a.tag_id,CASE  WHEN a.sync_flag = 0 THEN "未分配"  ELSE "已分配" END AS sync_status,CASE  WHEN a.finish = 0 THEN "未完成"  ELSE "已完成" END AS review_status,b.name as tag_name from task a left join tag b on a.tag_id = b.id where a.delflag=0 and a.createuser_id=%s''' % request.user.id
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
    result['aaData'] = items
    result['iTotalRecords'] = count
    result["iTotalDisplayRecords"] = count
    return HttpResponse(json.dumps(result), content_type="application/json")


def save(request):
    rank = None
    sid = request.POST.get('id')
    start = request.POST.get('start', 0)
    end = request.POST.get('end', 0)

    if int(start) > int(end):
        result = {"ret": 10000, "status": "failed", "msg": "评论间隔的开始时间不能大于结束时间"}
        return HttpResponse(json.dumps(result), content_type="application/json")

    try:
        if sid:
            rank = Task.objects.get(id=sid)
            if rank.sync_flag == 1:
                result = {"ret": 10000, "status": "failed", "msg": "任务已分配,无法进行修改!"}
                return HttpResponse(json.dumps(result), content_type="application/json")
    except Task.DoesNotExist:
        pass
    if rank:
        option = request.POST.get("option")
        if int(option):
            accounts = Account.objects.filter(delflag=0, tag_id=request.POST.get('tag'), createuser_id=5)
            if accounts.count() == 0:
                result = {"ret": 10000, "status": "failed", "msg": "当前系统下没有买手号,请联系客服!"}
                return HttpResponse(json.dumps(result), content_type="application/json")
            integral = 100
        else:
            accounts = Account.objects.filter(delflag=0, tag_id=request.POST.get('tag'), createuser_id=request.user.id,enable_review=0)
            if accounts.count() == 0:
                result = {"ret": 10000, "status": "failed", "msg": "当前账号下没有买手号!"}
                return HttpResponse(json.dumps(result), content_type="application/json")
        form = TaskForm(request.POST or None, instance=rank)
    else:
        option = request.POST.get("option")
        comment = request.POST.get("comment")#.replace('∣', '|').replace("‘", "'").replace(',', ',').replace('｜', '|')
        comments = comment.strip().strip('\r\n').split('\r\n')
        for com in comments:
            coms = com.split('|')
            if len(coms) != 2:
                result = {"ret": 10000, "status": "failed", "msg": "请输入正确的评论格式(标点符号为英文符号),错误的评论为:%s" % com}
                return HttpResponse(json.dumps(result), content_type="application/json")
        total = request.POST.get('total')
        if int(total) > len(comments):
            result = {"ret": 10000, "status": "failed", "msg": "输入的评论总数大于设置的评论条数!"}
            return HttpResponse(json.dumps(result), content_type="application/json")
        if int(option):
            accounts = Account.objects.filter(delflag=0, tag_id=request.POST.get('tag'), createuser_id=5,enable_review=0)
            if accounts.count() == 0:
                result = {"ret": 10000, "status": "failed", "msg": "当前系统下没有买手号,请联系客服!"}
                return HttpResponse(json.dumps(result), content_type="application/json")
            integral = 100
        else:
            accounts = Account.objects.filter(delflag=0, tag_id=request.POST.get('tag'), createuser_id=request.user.id)
            if accounts.count() == 0:
                result = {"ret": 10000, "status": "failed", "msg": "当前账号下没有买手号!"}
                return HttpResponse(json.dumps(result), content_type="application/json")
            discount = request.user.user_profile.discount
            integral = int(30 * (discount / 100.0))
        total_integral = integral * len(comments)
        if Profile.objects.get(user_id=request.user.id).integral < total_integral:
            result = {"ret": 10000, "status": "failed", "msg": "当前账号积分不足!"}
            return HttpResponse(json.dumps(result), content_type="application/json")
        form = TaskForm(request.POST or None)
    if form.is_valid():
        instance = form.save(commit=False)
        instance.start = start
        instance.end = end
        if sid:
            instance.updateuser = request.user
        else:
            instance.createuser = request.user
        instance.save()
        # if sid:
        #     Log.objects.create(user_id=request.user.id, ctype=2, operation=1, desc=u"修改标签:" + name)
        # else:
        #     Log.objects.create(user_id=request.user.id, ctype=2, operation=0, desc=u"新增标签:" + name)
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
    rank = None
    try:
        if request.POST.get('id'):
            rank = Task.objects.get(id=request.POST.get('id'))
            if rank.sync_flag == 1:
                result = {"ret": 10000, "status": "failed", "msg": "任务已分配,无法进行删除!"}
                return HttpResponse(json.dumps(result), content_type="application/json")
    except Task.DoesNotExist:
        pass
    if rank:
        try:
            rank.delflag = 1
            rank.save()
            result = {"ret": 0, "status": "success"}
            return HttpResponse(json.dumps(result), content_type="application/json")
        except:
            pass
    return HttpResponse(json.dumps({"ret": 10000, "status": "failed"}), content_type="application/json")


def batchdelete(request):
    ids = request.POST.get('ids').split(",")
    try:
        if ids:
            with transaction.atomic():
                for sid in ids:
                    tag = Task.objects.get(id=sid)
                    tag.delflag = 1
                    tag.save()
        result = {"ret": 0, "status": "success"}
        return HttpResponse(json.dumps(result), content_type="application/json")
    except Exception, ex:
        return HttpResponse(json.dumps({"ret": 10000, "status": "failed", "msg": str(ex)}), content_type="application/json")


def log(request):
    if request.user.is_authenticated():
        if request.user.user_profile.is_active:
            pwd_forms = ChangeForm()
            sql = 'select a.*,CONCAT(left(a.content,30),"...") as content,CASE  WHEN status= 0 THEN "未检测"  ELSE "成功" END AS review_status,b.name from task_log a left join account b on a.account_id= b.id where a.createuser_id=%s order by a.id desc' % request.user.id
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
            template = loader.get_template('review_log.html')
            context = {"review_log": "active", "pwd_forms": pwd_forms, "username": request.user.username, "logs": items}
            return HttpResponse(template.render(context, request))
        else:
            return HttpResponseRedirect('/notice/')
    else:
        return HttpResponseRedirect('/login/')

def log_bak(request):
    if request.user.is_authenticated():
        pwd_forms = ChangeForm()
        sql = 'select a.*,CONCAT(left(a.content,30),"...") as content,CASE  WHEN status= 0 THEN "未检测"  ELSE "成功" END AS review_status,b.name from task_log a left join account b on a.account_id= b.id where a.createuser_id=%s order by a.id desc' % request.user.id
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
        template = loader.get_template('review_log.html')
        context = {"review_log": "active", "pwd_forms": pwd_forms, "username": request.user.username, "logs": items}
        return HttpResponse(template.render(context, request))
    else:
        return HttpResponseRedirect('/login/')
