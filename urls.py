from django.conf.urls import url
from views import *

urlpatterns = [
    url(r'^index', index),
    url(r'^source/', source),
    url(r'^save', save),
    url(r'^upload', upload),
    url(r'^delete', delete),
    url(r'^batchdelete', batchdelete),
]

