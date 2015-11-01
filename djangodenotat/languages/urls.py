# -*- coding: utf-8 -*-
from django.conf.urls import *

urlpatterns = patterns(
    'djangodenotat.languages.views',
    url(r'^$', 'translation.index', {'template_name': 'index.html'}, 'home'),
    url(r'^translate/$', 'translation.trans', {}, 'trans'),
    url(r'^load/$', 'admin.load', {}, 'load'),
    url(r'^bleu/$', 'admin.evaluation', {}, 'evaluation'),
)

