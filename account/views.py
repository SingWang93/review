# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import loader, HttpResponse,HttpResponseRedirect
import json
from django.views.decorators.csrf import csrf_exempt
from django.db import connection, transaction, IntegrityError
from datetime import datetime
import urlparse
import random
import time
from Crypto.Cipher import AES
import base64
import paramiko
import csv
import urllib2
from bs4 import BeautifulSoup
from forms import AccountForm
from tag.models import Tag
from profiles.models import Profile
from account.models import Account
from django.contrib.auth.models import User
from review.views import ChangeForm


# Create your views here.

def encrypt(source, key, iv):
    PADDING = "\0"
    pad_it = lambda s: s + (16 - len(s) % 16) * str(PADDING)
    generator = AES.new(key, AES.MODE_CBC, iv)
    crypt = generator.encrypt(pad_it(source))
    return base64.b64encode(crypt)


def decrypt(source, key, iv):
    PADDING = "\0"
    generator = AES.new(key, AES.MODE_CBC, iv)
    recovery = generator.decrypt(base64.b64decode(source))
    return recovery.rstrip(PADDING)



def index(request):
    if request.user.is_authenticated():
        if request.user.user_profile.is_active:
            pwd_forms = ChangeForm()
            forms = AccountForm()
            tags = Tag.objects.all()
            template = loader.get_template('account.html')
            context = {"account": "active", "forms": forms, "tags": tags, "username": request.user.username, "pwd_forms":pwd_forms}
            return HttpResponse(template.render(context, request))
        else:
            return HttpResponseRedirect('/notice/')
    else:
        return HttpResponseRedirect('/login/')


def index_bak(request):
    pwd_forms = ChangeForm()
    forms = AccountForm()
    tags = Tag.objects.all()
    template = loader.get_template('account.html')
    context = {"account": "active", "forms": forms, "tags": tags, "username": request.user.username, "pwd_forms":pwd_forms}
    return HttpResponse(template.render(context, request))


def source(request):
    result = {}
    iDisplayStart = int(request.GET.get('iDisplayStart', 1))
    iDisplayLength = int(request.GET.get('iDisplayLength', 20))
    keyword = request.GET.get('keyword', '')
    sql = '''SELECT a.id,a.name,CASE  WHEN a.cookies IS NULL OR a.cookies = "" THEN "X"  ELSE "Y" END AS cookies_status,a.email,a.cookies,a.password,CASE a.enable_cookie WHEN 0 THEN "未检测" WHEN 1 THEN "是" ELSE "否" END AS enable_cookie,CASE a.enable_review WHEN 0 THEN "未检测" WHEN 1 THEN "是" ELSE "否" END AS enable_review,a.tag_id AS tag,b.name AS tag_name FROM account a LEFT JOIN tag b ON a.tag_id = b.id WHERE a.createuser_id=%s AND a.delflag=0''' % request.user.id
    cursor = connection.cursor()
    if keyword:
        sql = sql + ' and (a.name like concat("%%",%s,"%%") or b.name like concat("%%",%s,"%%"))'
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
    # print connection.queries
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
    name = request.POST.get('name')
    tag = request.POST.get('tag')
    profile = Profile.objects.get(user_id=request.user.id)
    try:
        if request.POST.get('id'): obj = Account.objects.get(id=request.POST.get('id'))
    except Account.DoesNotExist:
        pass
    if obj:
        form = AccountForm(request.POST or None, instance=obj)
    else:
        form = AccountForm(request.POST or None)
    if form.is_valid():
        instance = form.save(commit=False)
        if request.POST.get('id'):
            instance.updateuser = request.user
            password = encrypt(request.POST.get('password'), profile.key[:8] + profile.iv[8:],
                               profile.key[8:] + profile.iv[:8])
            if password != obj.password:
                instance.password = password

        else:
            instance.createuser = request.user
        instance.tag_id = tag
        instance.password = encrypt(request.POST.get('password'), profile.key[:8] + profile.iv[8:],
                                    profile.key[8:] + profile.iv[:8])
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


def url2Dict(url):
    query = urlparse.urlparse(url).query
    return dict([(k, v[0]) for k, v in urlparse.parse_qs(query).items()])


def upload(request):
    f = request.FILES['file']
    datas = csv.reader(f)
    title = datas.next()
    tag = request.POST.get('tag')
    mode = int(request.POST.get('mode', 0))
    cu = connection.cursor()
    profile = Profile.objects.get(user_id=request.user.id)
    if 'name,email,password,cookies' == ','.join(title):
        items = []
        name = ""
        for line in datas:
            items.append(dict(zip(title, line)))
        try:
            with transaction.atomic():
                for item in items:
                    if item:
                        new_cookies = []
                        name = item.get('name', '').strip()
                        email = item.get('email', '').strip()
                        password = item.get('password', '').strip()
                        cookies = item.get('cookies', '').strip('"').strip().replace('\\n', ';').strip(";")
                        if cookies:
                            try:
                                jcookies = json.loads(cookies)
                                for cookie in jcookies:
                                    jcookie = {}
                                    domain = cookie.get('domain')
                                    expiry = cookie.get('expirationDate', cookie.get('Expires', cookie.get('expiry')))
                                    if isinstance(expiry, float):
                                        expiry = str(int(expiry))
                                    if not isinstance(expiry, int):
                                        if not expiry.isdigit():
                                            expiry = str(int(
                                                time.mktime(datetime.strptime(expiry, '%d %b %Y %X GMT').timetuple())))

                                    HttpOnly = cookie.get('hostOnly', cookie.get('HttpOnly', 'false'))
                                    cname = cookie.get('name')
                                    path = cookie.get('path', '/')
                                    secure = cookie.get('secure', 'false')
                                    value = cookie.get('value')
                                    jcookie['Domain'] = domain
                                    jcookie['Expiry'] = expiry
                                    jcookie['Name'] = cname
                                    jcookie['Value'] = value
                                    jcookie['Path'] = path
                                    jcookie['HttpOnly'] = HttpOnly
                                    jcookie['Secure'] = secure
                                    new_cookies.append(jcookie)
                            except:
                                lcookies = []
                                if '\n' in cookies:
                                    lcookies = cookies.split('\n')
                                elif ';' in cookies:
                                    lcookies = cookies.split(';')
                                for cookie in lcookies:
                                    jcookie = {}
                                    c = cookie.strip()
                                    if '\t' in c:
                                        c = c.split('\t')
                                    elif ' ' in c:
                                        c = c.split(' ')
                                    expiry = c[4]
#                                    if not expiry.isdigit():
#                                        expiry = str(
#                                            int(time.mktime(datetime.strptime(expiry, '%d %b %Y %X GMT').timetuple())))
                                    jcookie['Domain'] = c[0]
                                    jcookie['Expiry'] = expiry
                                    jcookie['Name'] = c[5]
                                    jcookie['Value'] = c[6]
                                    jcookie['Path'] = c[2]
                                    jcookie['HttpOnly'] = c[1]
                                    jcookie['Secure'] = c[3]
                                    new_cookies.append(jcookie)
                        new_cookies = json.dumps(json.loads(json.dumps(new_cookies)))
                        password = encrypt(password, profile.key[:8] + profile.iv[8:], profile.key[8:] + profile.iv[:8])
                        if mode == 0:
                            sql = 'insert into account(name,email,password,cookies,tag_id,createtime,createuser_id,delflag,enable_cookie,enable_review,review_flag) values (%s,%s,%s,%s,%s,%s,%s,0,0,0,1)'
                            cu.execute(sql, (name, email, password, new_cookies, tag, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), request.user.id))
                        elif mode == 1:
                            sql = 'update account set email=%s,password=%s,cookies=%s,updatetime=%s,updateuser_id=%s where name=%s and tag_id=%s and createuser_id=%s and delflag=0'
                            cu.execute(sql, (email, password, new_cookies, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), request.user.id, name, tag, request.user.id))
        except IntegrityError:
            result = {"ret": 10001, "status": "failed", "msg": u"账号:%s 已存在" % name}
            return HttpResponse(json.dumps(result), content_type="application/json")

        except Exception, ex:
            result = {"ret": 10001, "status": "failed", "msg": u"账号:%s出错,出错原因:%s" % (name, str(ex))}
            return HttpResponse(json.dumps(result), content_type="application/json")
        result = {"ret": 0, "status": "success"}
        # Log.objects.create(user_id=request.user.id, ctype=1, operation=1, desc=u"批量导入账号,批次号为:%s" % batchno)
    else:
        result = {"ret": 10000, "status": "failed", "msg": u"文件格式错误"}
    return HttpResponse(json.dumps(result), content_type="application/json")


def delete(request):
    obj = None
    try:
        if request.POST.get('id'): obj = Account.objects.get(id=request.POST.get('id'))
    except Account.DoesNotExist:
        pass
    if obj:
        try:
            obj.delflag = 1
            obj.save()
            result = {"ret": 0, "status": "success"}
            # Log.objects.create(user_id=request.user.id, ctype=1, operation=2, desc=u"删除账号:" + obj.name)
            return HttpResponse(json.dumps(result), content_type="application/json")
        except:
            pass
    return HttpResponse(json.dumps({"ret": 10000, "status": "failed"}), content_type="application/json")


def batchdelete(request):
    ids = request.POST.get('ids').split(",")
    try:
        if ids:
            names = []
            for sid in ids:
                with transaction.atomic():
                    obj = Account.objects.get(id=sid)
                    obj.delflag = 1
                    obj.save()
                    names.append(obj.name)
            # Log.objects.create(user_id=request.user.id, ctype=1, operation=2, desc=u"批量删除账号:" + ','.join(names))
        result = {"ret": 0, "status": "success"}
        return HttpResponse(json.dumps(result), content_type="application/json")
    except Exception, ex:
        return HttpResponse(json.dumps({"ret": 10000, "status": "failed", "msg": str(ex)}), content_type="application/json")


def log(request):
    parameter = request.GET
    data = parameter.get('d')
    token = parameter.get('token')
    try:
        data = json.loads(decrypt(data, token[0:16], token[3:19]))
        uid = data.get('id')
        user = User.objects.get(id=uid)
        username = data.get('username')
        if user.user_profile.token == token and user.username == username:
            cur_user = data.get('cur_user')
            bname = data.get('bname')
            bemail = data.get('bemail')
            # Log.objects.create(user_id=uid, ctype=1, operation=4, desc=u"用户:%s 打开账号:%s 邮箱为:%s" % (cur_user, bname, bemail))
            return HttpResponse(json.dumps({"ret": 0, "status": "success"}), content_type="application/json")
    except:
        return HttpResponse(json.dumps({"ret": 10000, "status": "failed"}), content_type="application/json")

