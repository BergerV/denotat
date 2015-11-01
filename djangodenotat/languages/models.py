# -*- coding: utf-8 -*-
from django.db import models
from djangodenotat.test.text_parser import split_n_gramm


class Language(models.Model):
    name = models.CharField(max_length=100, verbose_name=u'Название')

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = u'язык'
        verbose_name_plural = u'языки'
                
                
class Ngramm(models.Model):
    n_gramm = models.TextField(db_index=True, verbose_name=u'N-грамма')
    n = models.IntegerField(db_index=True, verbose_name=u'Длина n-граммы')
    lang = models.ForeignKey(Language, verbose_name=u'Язык')
    frequence = models.FloatField(default=0.0, verbose_name=u'Вероятность n-граммы')

    def get_n(self):
        return len(split_n_gramm(self.n_gramm))  
    
    def __unicode__(self):
        return self.n_gramm + ' ' + self.lang.__unicode__()    

    class Meta:
        verbose_name = u'n-грамма'
        verbose_name_plural = u'n-граммы'


class Translation(models.Model):
    orig = models.TextField(db_index=True, verbose_name=u'Оригинал')
    lang_orig = models.ForeignKey(Language, related_name=u'lang_orig', verbose_name=u'Язык оригинала')
    trans = models.TextField(db_index=True, verbose_name=u'Перевод')
    lang_trans = models.ForeignKey(Language, related_name=u'lang_trans', verbose_name=u'Язык перевода')
    probability = models.FloatField(default=0.5, db_index=True, verbose_name=u'Вероятность перевода')
    
    def __unicode__(self):
        return self.orig + ' ' + self.trans + ' ' + str(self.probability)    

    class Meta:
        verbose_name = u'перевод'
        verbose_name_plural = u'переводы'
