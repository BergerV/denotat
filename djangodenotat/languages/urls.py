# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *

urlpatterns = patterns('diploma2.languages.views',    
    url(r'^$', 'translation.index', {'template_name': 'index.html'},'home'),    
    url(r'^translate/$','translation.trans',{},'trans'),
    url(r'^load/$','admin.load',{},'load'),
    url(r'^bleu/$','admin.evaluation',{},'evaluation'),
)

