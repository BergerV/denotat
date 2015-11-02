# -*- coding: utf-8 -*-
from django.conf.urls import *

urlpatterns = patterns(
    'djangodenotat.denotat.views',
    url(r'^essay/$', 'essay.essay', {}, 'essay')
)

