from django.conf.urls import url
from views import *

urlpatterns = [
    url(r'^index', index),
    url(r'^source/', source),
    url(r'^save', save),
    url(r'^upload/', upload),
    url(r'^insert/', insert),
    url(r'^delete', delete),
    url(r'^log', log),
    url(r'^get_buyers', get_buyers),
    url(r'^update_quantity', update_quantity),
    url(r'^insert_log',insert_log),
    url(r'^update_buyer',update_buyer),
]


