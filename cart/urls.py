from django.conf.urls import url
from views import *

urlpatterns = [
    url(r'^index', index),
    url(r'^tutorial', tutorial),
    url(r'^source/', source),
    url(r'^save', save),
    url(r'^delete', delete),
    url(r'^log', log),
]

