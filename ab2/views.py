# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render, loader, HttpResponse, redirect, HttpResponseRedirect
from forms import Ab2Form
from django.db import connection, transaction
import datetime
import json
from models import *
from profiles.models import *
from tag.models import Tag
from review.views import ChangeForm
from django.views.decorators.csrf import csrf_exempt
import csv


# Create your views here.
def index(request):
    if request.user.is_authenticated():
        if request.user.user_profile.is_active:
            forms = Ab2Form()
            cursor = connection.cursor()
            sql = "select count(id) from ab3_log where msg like \"加购成功%%\" and createtime between %s and %s"
            params = []
            params.append((datetime.datetime.now() + datetime.timedelta(hours=0)).strftime('%Y-%m-%d 00:00:00'))
            params.append((datetime.datetime.now()+ datetime.timedelta(hours=0)).strftime('%Y-%m-%d 23:59:59'))
            cursor.execute(sql,params)
            d1_count = cursor.fetchall()[0][0]
            sql = "select count(id) from ab3_log where msg like \"加购成功%%\" and createtime between %s and %s"
            params = []
            params.append((datetime.datetime.now() + datetime.timedelta(hours=0)).strftime('%Y-%m-%d %H:00:00'))
            params.append((datetime.datetime.now()+ datetime.timedelta(hours=0)).strftime('%Y-%m-%d %H:59:59'))
            cursor.execute(sql,params)
            h1_count = cursor.fetchall()[0][0]      
            pwd_forms = ChangeForm()
            tags = Tag.objects.all()
            template = loader.get_template('ab2.html')
            context = {"ab2": "active", "forms": forms, "pwd_forms": pwd_forms, "username": request.user.username,"tags":tags,"d1_count":d1_count,"h1_count":h1_count}
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
    sql = 'select a.quantity,a.id,a.url,a.asin,a.total,b.name as tag_name,a.createtime,a.starttime,a.sync_flag,CASE  WHEN a.sync_flag = 0 THEN "未分配"  ELSE "已分配" END AS sync_status from ab2 a left join tag b on a.tag_id = b.id where a.delflag=0 and a.createuser_id=%s' % request.user.id
    cursor = connection.cursor()
    if keyword:
        sql = sql + ' and  a.keyword like concat("%%",%s,"%%")'
        count = cursor.execute(sql, (keyword, keyword))
    else:
        count = cursor.execute(sql)

    start = (iDisplayStart / iDisplayLength) * iDisplayLength
    sql += ' order by id desc limit %s,%s'
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
            if isinstance(v, datetime.datetime):
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
            obj = AB2.objects.get(id=sid)
            if obj.sync_flag == 1:
                result = {"ret": 10000, "status": "failed", "msg": "任务已分配,无法进行修改!"}
                return HttpResponse(json.dumps(result), content_type="application/json")
    except Ab2.DoesNotExist:
        pass
    if obj:
        form = Ab2Form(request.POST or None, instance=obj)
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
        form = Ab2Form(request.POST or None)
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
            obj = Ab2.objects.get(id=request.POST.get('id'))
            if obj.sync_flag == 1:
                result = {"ret": 10000, "status": "failed", "msg": "任务已分配,无法进行删除!"}
                return HttpResponse(json.dumps(result), content_type="application/json")
    except Ab.DoesNotExist:
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
                    if isinstance(v, datetime.datetime):
                        data[k] = v.strftime('%Y-%m-%d %H:%M:%S')
                items.append(data)
            template = loader.get_template('cart_log.html')
            context = {"cart_log": "active", "pwd_forms": pwd_forms, "username": request.user.username, "logs": items}
            return HttpResponse(template.render(context, request))
        else:
            return HttpResponseRedirect('/notice/')
    else:
        return HttpResponseRedirect('/login/')



@csrf_exempt
def insert(request):
    result = {}
    #return HttpResponse(request.POST.get("tasks"))
    tasks = json.loads(request.POST.get("tasks",[{}]))
    cursor = connection.cursor()
    for task in tasks:
        asin = task.get('asin')
        keyword = task.get('keyword')
        brand = task.get('brand')
        total = task.get('total')
        starttime = task.get('starttime')
        p = task.get('platform')
        params = []
        sql = "insert into ab2(keyword,asin,brand,total,createtime,starttime,delflag,finish,sync_flag,createuser_id,tag_id) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        params.append(keyword)
        params.append(asin)
        params.append(brand)
        params.append(total)
        params.append(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        params.append(starttime)
        params.append(0)
        params.append(0)
        params.append(0)
        params.append(5)
        if p == 'us':
            params.append(1)
        elif p == 'uk':
            params.append(11)
        else:
            params.append(1)
        cursor.execute(sql,params)
        result['ret'] = 0
        result['status'] = 'success'
    return HttpResponse(json.dumps(result), content_type="application/json")



@csrf_exempt
def upload(request):
    f = request.FILES['file']
    datas = csv.reader(f)
    title = datas.next()
    tag = request.POST.get('tag')
    cursor = connection.cursor()
    result = {}
    if 'url,asin,starttime,total,platform' == ','.join(title).strip().strip(","):
        items = []
        for line in datas:
            items.append(dict(zip(title, line)))
        try:
            with transaction.atomic():
                for item in items:
                    if item:
                        url = item.get('url', '').strip()
                        if not url:
                            continue
                        asin = item.get('asin', '').strip()
                        asin = item.get('asin', '').strip()
                        total = item.get('total', '').strip()
                        starttime = item.get('starttime', '').strip()
                        p = item.get('platform', '').strip()
                        params = []
                        sql = "insert into ab2(url,asin,total,createtime,starttime,delflag,finish,sync_flag,createuser_id,tag_id) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
                        params.append(url)
                        params.append(asin)
                        params.append(total)
                        params.append(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                        params.append(starttime)
                        params.append(0)
                        params.append(0)
                        params.append(0)
                        params.append(request.user.id)
                        if p == 'us':
                            params.append(1)
                        elif p == 'uk':
                            params.append(11)
                        else:
                            params.append(1)
                        cursor.execute(sql,params)
                        result['ret'] = 0
                        result['status'] = 'success'
            return HttpResponse(json.dumps(result), content_type="application/json")
        except Exception, ex:
            return HttpResponse(json.dumps({"ret":10000,"staus":"failed","msg":str(ex)}), content_type="application/json")

    else:
        return HttpResponse(json.dumps({"ret":10000,"staus":"failed","msg":"文件格式出错"}), content_type="application/json")





@csrf_exempt
def get_buyers(request):
    result = {}
    asin = request.GET.get('asin', '')
    sql = "select id,name from buyer where status = 0 and id not in (select a.buyer_id from ab3_log a left join ab2 b on a.ab2_id=b.id where contains(b.asin ,%s))"# limit 0,100"
    params = []
    cursor = connection.cursor()
    params.append(asin)
    cursor.execute(sql,params)
    results = cursor.fetchall()
    columns = [column[0] for column in cursor.description]
    datas = []
    for row in results:
        datas.append(dict(zip(columns, row)))

    items = []
    for data in datas:
        for k, v in data.iteritems():
            if isinstance(v, datetime.datetime):
                data[k] = v.strftime('%Y-%m-%d %H:%M:%S')
        items.append(data)
    result['datas'] = items
    return HttpResponse(json.dumps(result), content_type="application/json")




@csrf_exempt
def update_quantity(request):
    result = {}
    task_id = request.GET.get('task_id', '')
    sql = "update ab2 set quantity = quantity+1 where id=%s"
    params = []
    cursor = connection.cursor()
    params.append(task_id)
    cursor.execute(sql,params)
    result['ret']=0
    result['status']='success'
    return HttpResponse(json.dumps(result), content_type="application/json")



@csrf_exempt
def insert_log(request):
    result = {}
    task_id = request.GET.get('task_id', '')
    buyer_id = request.GET.get('buyer_id', '')
    buyer_name = request.GET.get('buyer_name','')
    status = request.GET.get('status', '')
    msg = request.GET.get('msg', '')
    ip = request.GET.get('ip')
    sql = "insert into ab3_log(ab2_id,createtime,buyer_id,status,msg,ip,buyer_name) values (%s,%s,%s,%s,%s,%s,%s)"
    params = []
    cursor = connection.cursor()
    params.append(task_id)
    params.append(datetime.datetime.now())# + datetime.timedelta(hours=8))
    params.append(buyer_id)
    params.append(status)
    params.append(msg.encode('utf-8'))
    params.append(ip)
    params.append(buyer_name)
    cursor.execute(sql,params)
    result['ret']=0
    result['status']='success'
    return HttpResponse(json.dumps(result), content_type="application/json")


@csrf_exempt
def update_buyer(request):
    result = {}
    buyer_id = request.GET.get('buyer_id', '')
    msg = request.GET.get("msg")
    status = request.GET.get("status")
    sql = "update buyer set status=%s,msg=%s where id=%s"
    params = []
    cursor = connection.cursor()
    params.append(status)
    params.append(msg)
    params.append(buyer_id)
    cursor.execute(sql,params)
    result['ret']=0
    result['status']='success'
    return HttpResponse(json.dumps(result), content_type="application/json")



def daily_server(request):
    if request.user.is_authenticated():
        if request.user.user_profile.is_active:
            pwd_forms = ChangeForm()
            template = loader.get_template('daily_server.html')
            context = {"daily_server": "active", "pwd_forms": pwd_forms, "username": request.user.username}
            return HttpResponse(template.render(context, request))
        else:
            return HttpResponseRedirect('/notice/')
    else:
        return HttpResponseRedirect('/login/')

def daily_buyer(request):
    if request.user.is_authenticated():
        if request.user.user_profile.is_active:
            pwd_forms = ChangeForm()
            template = loader.get_template('daily_buyer.html')
            context = {"daily_buyer": "active", "pwd_forms": pwd_forms, "username": request.user.username}
            return HttpResponse(template.render(context, request))
        else:
            return HttpResponseRedirect('/notice/')
    else:
        return HttpResponseRedirect('/login/')


def source_buyer(request):
    result = {}
    iDisplayStart = int(request.GET.get('iDisplayStart', 1))
    iDisplayLength = int(request.GET.get('iDisplayLength', 20))
    cursor = connection.cursor()
    sql = "select buyer_id,count(buyer_id) as total from ab3_log where createtime between %s and %s and msg like \"加购成功%%\" group by buyer_id order by total desc"
    start = (iDisplayStart / iDisplayLength) * iDisplayLength
    params = []
    params.append((datetime.datetime.now() - datetime.timedelta(hours=0)).strftime('%Y-%m-%d 00:00:00'))
    params.append((datetime.datetime.now() - datetime.timedelta(hours=0)).strftime('%Y-%m-%d 23:59:59'))
    count = cursor.execute(sql,params)
    #params.append(start)
    #sql += ' limit %s,%s'
    #params.append(iDisplayLength)
    #cursor.execute(sql,params)
    results = cursor.fetchall()
    columns = [column[0] for column in cursor.description]
    datas = []
    for row in results:
        datas.append(dict(zip(columns, row)))

    items = []
    for data in datas:
        for k, v in data.iteritems():
            if isinstance(v, datetime.datetime):
                data[k] = v.strftime('%Y-%m-%d %H:%M:%S')
        items.append(data)
    result['aaData'] = items
    result['iTotalRecords'] = count
    result["iTotalDisplayRecords"] = count
    return HttpResponse(json.dumps(result), content_type="application/json")



def source_server(request):
    result = {}
    iDisplayStart = int(request.GET.get('iDisplayStart', 1))
    iDisplayLength = int(request.GET.get('iDisplayLength', 20))
    cursor = connection.cursor()
    sql ="select ip,count(ip) as total from ab3_log where createtime between %s and %s and msg like \"加购成功%%\" group by ip order by total desc"
    start = (iDisplayStart / iDisplayLength) * iDisplayLength
    params = []
    params.append((datetime.datetime.now() - datetime.timedelta(hours=0)).strftime('%Y-%m-%d 00:00:00'))
    params.append((datetime.datetime.now() - datetime.timedelta(hours=0)).strftime('%Y-%m-%d 23:59:59'))
    count = cursor.execute(sql,params)
    #sql += ' limit %s,%s'
    #params.append(start)
    #params.append(iDisplayLength)
    #cursor.execute(sql,params)
    results = cursor.fetchall()
    columns = [column[0] for column in cursor.description]
    datas = []
    for row in results:
        datas.append(dict(zip(columns, row)))

    items = []
    for data in datas:
        for k, v in data.iteritems():
            if isinstance(v, datetime.datetime):
                data[k] = v.strftime('%Y-%m-%d %H:%M:%S')
        items.append(data)
    result['aaData'] = items
    result['iTotalRecords'] = count
    result["iTotalDisplayRecords"] = count
    return HttpResponse(json.dumps(result), content_type="application/json")
