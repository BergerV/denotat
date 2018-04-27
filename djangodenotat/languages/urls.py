# -*- coding: utf-8 -*-
from django.conf.urls import *
from djangodenotat.languages.views import translation, admin

urlpatterns = [
    url(r'^$', translation.index, {'template_name': 'index.html'}, name='home'),
    url(r'^translate/$', translation.trans, {}, name='trans'),
    url(r'^load/$', admin.load, {}, name='load'),
    url(r'^bleu/$', admin.evaluation, {}, name='evaluation'),
]

