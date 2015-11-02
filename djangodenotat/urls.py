#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.conf.urls import *
from django.conf import settings
from djangodenotat.languages.views import *
# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^', include('djangodenotat.languages.urls')),
    url(r'^', include('djangodenotat.denotat.urls')),
)

#if settings.DEBUG:
urlpatterns += patterns('',
                        (r'^media/(?P<path>.*)',
                         'django.views.static.serve',
                         {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}
                         ),
                        )
