# -*- coding:utf-8 -*-

from django.contrib import admin
from djangodenotat.languages.models import *


class LangAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
    list_display_links = ['id']
    search_fields = ['name']


class TextAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'words_count', 'lang']
    list_display_links = ['id']
    search_fields = ['title', 'lang']


class NgrammAdmin(admin.ModelAdmin):
    list_display = ['n', 'n_gramm', 'lang', 'frequency']
    list_display_links = ['n_gramm']   
    search_fields = ['n_gramm', 'lang__name']


class TransAdmin(admin.ModelAdmin):
    list_display = ['id', 'orig', 'lang_orig', 'trans', 'lang_trans', 'probability']
    list_display_links = ['id']   
    search_fields = ['orig', 'trans', 'lang_orig__name', 'lang_trans__name', 'probability']


admin.site.register(Text, TextAdmin)
admin.site.register(Language, LangAdmin)
admin.site.register(Ngramm, NgrammAdmin)
admin.site.register(Translation, TransAdmin)
