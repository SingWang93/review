# -*- coding:utf-8 -*-
from django.shortcuts import render, HttpResponseRedirect, render_to_response, HttpResponse, loader
from django.contrib import auth
from django import forms
import json
import string
import random
from profiles.models import Profile
from django.db import transaction
from account.models import *
from task.models import *
from package.models import Package, Order
from integral.models import Integral
from alipay import Alipay
import time
from datetime import datetime
from django.db import connection
from django.views.decorators.csrf import csrf_exempt

domain = "http://52.80.104.236:8082"

def index(request):
    if request.user.is_authenticated():
        if request.user.user_profile.is_active:
            user = request.user
            pwd_forms = ChangeForm()
            total = Account.objects.filter(createuser=user, delflag=0).count()
            total_cookie = Account.objects.filter(createuser=user, delflag=0, enable_cookie=1).count()
            total_review = Account.objects.filter(createuser=user, delflag=0, enable_review=1).count()
            sql = '''SELECT a.id,a.tag_id as tag,CASE  WHEN a.`mode` = "A" THEN "ASIN"  ELSE "SELLERID" END AS `mode_type`,a.mode,a.total,a.createtime,a.starttime,a.keyword,CONCAT(left(a.comment,30),"...") as content,a.comment,a.tag_id,CASE  WHEN a.sync_flag = 0 THEN "未分配"  ELSE "已分配" END AS sync_status,CASE  WHEN a.finish = 0 THEN "未完成"  ELSE "已完成" END AS review_status,b.name as tag_name from task a left join tag b on a.tag_id = b.id where a.delflag=0 and a.createuser_id=%s order by id desc limit 0,10''' % request.user.id
            cursor = connection.cursor()
            cursor.execute(sql)
            results = cursor.fetchall()
            columns = [column[0] for column in cursor.description]
            datas = []
            for row in results:
                datas.append(dict(zip(columns, row)))

            reviews = []
            for data in datas:
                for k, v in data.iteritems():
                    if isinstance(v, datetime):
                        data[k] = v.strftime('%Y-%m-%d %H:%M:%S')
                reviews.append(data)
            integral = Profile.objects.get(user_id=user.id).integral
            template = loader.get_template('index.html')
            context = {"username": request.user.username, "pwd_forms": pwd_forms, "reviews": reviews, "total": total, "total_cookie": total_cookie, "total_review": total_review, "integral": integral}
            return HttpResponse(template.render(context, request))
        else:
            return HttpResponseRedirect('/notice/')
    else:
        return HttpResponseRedirect('/login/')


def login(request):
    template = loader.get_template('login.html')
    context = {}
    if request.method.lower() == "get":
        if not request.user.is_authenticated():
            return HttpResponse(template.render(context, request))
        return HttpResponseRedirect('/index.html')
    else:
        username = request.POST['username']
        password = request.POST['password']
        user = auth.authenticate(request, username=username, password=password)
        if user is not None and user.is_active:
            auth.login(request, user)
            request.session['username'] = user.get_full_name()
            return HttpResponseRedirect('/index')
        else:
            context['ret'] = 10000
            context['msg'] = u"用户名或密码错误!"
            return HttpResponse(template.render(context, request))


def logout(request):
    auth.logout(request)
    return HttpResponseRedirect('/login/')


class ChangeForm(forms.Form):
    old_password = forms.CharField(label='原密码', widget=forms.PasswordInput())
    new_password = forms.CharField(label='新密码', widget=forms.PasswordInput())


def change_pass(request):
    uf = ChangeForm(request.POST)
    result = {}
    if uf.is_valid():
        username = request.user.username
        old_password = request.POST.get('old_password', '')
        new_password = request.POST.get('new_password', '')
        user = auth.authenticate(username=username, password=old_password)
        if user is not None and user.is_active:
            user.set_password(new_password)
            user.save()
            result = {"ret": 0, "status": "success", "msg": u"密码修改成功,请退出后登陆"}
            auth.logout(request)
        else:
            result = {"ret": 10000, "status": "failed", "msg": u"请检查原密码是否输入正确"}
    return HttpResponse(json.dumps(result), content_type="application/json")


def regist(request):
    template = loader.get_template('regist.html')
    context = {}
    return HttpResponse(template.render(context, request))


def create(request):
    username = request.POST.get('username')
    password = request.POST.get('password')
    if username or password:
        try:
            User.objects.get(username=username)
            template = loader.get_template('regist.html')
            context = {"msg": "用户名已存在"}
            return HttpResponse(template.render(context, request))
        except:
            user = User.objects.create(username=username)
            user.set_password(password)
            user.save()
            key = ''.join(random.sample(string.ascii_letters + string.digits, 16))
            iv = ''.join(random.sample(string.ascii_letters + string.digits, 16))
            token = ''.join(random.sample(string.ascii_letters + string.digits, 24))
            Profile.objects.create(user_id=user.id, key=key, iv=iv, token=token, is_active=0)
    else:
        template = loader.get_template('regist.html')
        context = {"msg": "用户名或密码不能为空"}
        return HttpResponse(template.render(context, request))
    return HttpResponseRedirect('/login/')


def create_bak(request):
    username = request.POST.get('username')
    password = request.POST.get('password')
    user = User.objects.create(username=username)
    user.set_password(password)
    user.save()
    key = ''.join(random.sample(string.ascii_letters + string.digits, 16))
    iv = ''.join(random.sample(string.ascii_letters + string.digits, 16))
    token = ''.join(random.sample(string.ascii_letters + string.digits, 24))
    Profile.objects.create(user_id=user.id, key=key, iv=iv, token=token, is_active=0)
    return HttpResponseRedirect('/login/')




def package(request):
    if request.user.is_authenticated():
        if request.user.user_profile.is_active:
            pwd_forms = ChangeForm()
            packages = Package.objects.filter(display=1)
            integrals = Integral.objects.filter(display=1)
            template = loader.get_template('package.html')
            context = {"packages": packages, "integrals": integrals, "username": request.user.username, "pwd_forms":pwd_forms}
            return HttpResponse(template.render(context, request))
        else:
            return HttpResponseRedirect('/notice/')
    else:
        return HttpResponseRedirect('/login/')


def pay(request):
    package_id = request.GET.get("setPackId")
    pay_type = request.GET.get('type')
    if package_id is not None:
        order_id = str(int(time.time() * 1000))
        package = Package.objects.get(id=package_id)
        if pay_type == "0":
            alipay = Alipay(pid='2088021435732027', key='g5eerb3z111h75kpo3mfa1cibacbloo6', seller_email='zixunwl@126.com')
            url = alipay.create_direct_pay_by_user_url(out_trade_no=order_id, subject=package.name + u" - 亚马逊辅助工具", total_fee=package.price, return_url=domain + '/alipay/return-url', notify_url=domain + '/alipay/notify-url')
            Order.objects.create(order_id=int(order_id), createuser=request.user, package=package, pay_method=pay_type)
            return HttpResponseRedirect(url)
    else:
        template = loader.get_template('404.html')
        context = {}
        return HttpResponse(template.render(context, request))

@csrf_exempt
def alipay_notity(request):
    data = request.POST
    out_trade_no = data.get("out_trade_no","")
    trade_status = data.get("trade_status","")
    seller_email = data.get('seller_email',"")
    seller_id = data.get('seller_id',"")
    if "2088021435732027" == seller_id and seller_email.replace("%40","@") == "zixunwl@126.com":
        if trade_status == "TRADE_SUCCESS":
            try:
                with transaction.atomic():
                    order = Order.objects.get(order_id=out_trade_no)
                    order.status = 1
                    order.save()
                    profile = Profile.objects.get(user_id=order.createuser_id)
                    package = Package.objects.get(id=order.package_id)
                    profile.integral = profile.integral + package.integral
                    profile.save()
                return HttpResponse("success")
            except Exception, ex:
                Task_log.objects.create(createuser_id=1,task_id=1,account_id=1,msg=str(ex))
                print ex
        return HttpResponse("fail")


def alipay_return(request):
    data = request.GET
    #data = dict(item.split('=') for item in datas.split("&"))
    out_trade_no = data.get("out_trade_no")
    trade_no = data.get("trade_no")
    trade_status = data.get("trade_status")
    seller_email = data.get('seller_email')
    seller_id = data.get('seller_id')
    #return HttpResponse("%s,%s,%s,%s,%s" % (trade_no,out_trade_no,trade_status,seller_email,seller_id))
    if "2088021435732027" == seller_id and seller_email.replace("%40","@") == "zixunwl@126.com":
        if trade_status == "TRADE_SUCCESS":
            return HttpResponseRedirect("/index")



def notice(request):
    template = loader.get_template('notice.html')
    context = {}
    return HttpResponse(template.render(context, request))





def userlist(request):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            pwd_forms = ChangeForm()
            template = loader.get_template('user.html')
            context = {"username": request.user.username, "pwd_forms": pwd_forms}
            return HttpResponse(template.render(context, request))
    template = loader.get_template('404.html')
    context = {}
    return HttpResponse(template.render(context, request))


def usersource(request):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            iDisplayStart = int(request.GET.get('iDisplayStart', 1))
            iDisplayLength = int(request.GET.get('iDisplayLength', 20))
            result = {}
            sql = 'select b.id,a.username,b.is_active,CASE WHEN b.is_active =1  THEN "激活"  ELSE "未激活" END AS status  from auth_user a left join profile b on a.id = b.user_id'
            cursor = connection.cursor()
            count = cursor.execute(sql)
            start = (iDisplayStart / iDisplayLength) * iDisplayLength
            sql += ' limit %s,%s'
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


def enableuser(request):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            uid = request.POST.get("id")
            profile = Profile.objects.get(id=uid)
            profile.is_active = 1
            profile.save()
            result = {"ret": 0, "status": "success"}
            return HttpResponse(json.dumps(result), content_type="application/json")



def disableuser(request):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            uid = request.POST.get("id")
            profile = Profile.objects.get(id=uid)
            profile.is_active = 0
            profile.save()
            result = {"ret": 0, "status": "success"}
            return HttpResponse(json.dumps(result), content_type="application/json")

