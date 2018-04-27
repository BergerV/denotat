# -*- coding: utf-8 -*-
from django.conf.urls import *
from djangodenotat.denotat.views import essay

urlpatterns = [
    url(r'^essay/$', essay.essay, {}, name='essay')
]

