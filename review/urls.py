"""review URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
'''
from django.conf.urls import url,include
import views
from task import views as tasks
from task import urls as task


urlpatterns = [
    url(r'^login/$', views.login),
    url(r'^logout/$', views.logout),
    url(r'^regist/$', views.regist),
    url(r'^create/$', views.create),
    url(r'^index/', views.index),
    url(r'task/',include(task)),
    url(r'^', views.index),
]
'''
from django.conf.urls import url,include
import views
from task import views as tasks
from task import urls as task
from account import urls as account
from cart import urls as cart
from ass import urls as ass
from ab import urls as ab
from ab2 import urls as ab2
from ac import urls as ac
from akh import urls as akh
from kw import urls as kw


urlpatterns = [
    url(r'^login/$', views.login),
    url(r'^logout/$', views.logout),
    url(r'^regist/$', views.regist),
    url(r'^create/$', views.create),
    url(r'^index/', views.index),
    url(r'^package/', views.package),
    url(r'^notice/', views.notice),
    url(r'^user/', views.userlist),
    url(r'^usersource/', views.usersource),
    url(r'^enableuser/', views.enableuser),
    url(r'^disableuser/', views.disableuser),
    url(r'^pay', views.pay),
    url(r'^alipay/return-url', views.alipay_return),
    url(r'^alipay/notify-url', views.alipay_notity),
    url(r'^buyer/source/',ab2.source_buyer),
    url(r'^server/source/',ab2.source_server),
    url(r'task/',include(task)),
    url(r'cart/',include(cart)),
    url(r'account/',include(account)),
    url(r'ass/',include(ass)),
    url(r'ab/',include(ab)),
    url(r'ab2/',include(ab2)),
    url(r'ac/',include(ac)),
    url(r'akh/',include(akh)),
    url(r'kw/',include(kw)),
    url(r'^', views.index),
]

