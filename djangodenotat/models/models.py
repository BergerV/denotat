#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.db import models

ORIENTATION_CHOICES = (
    ('10', '<--'),
    ('01', '-->'),
    ('11', '<->'),
)

class Text(models.Model):
    title = models.CharField(verbose_name=u'название')
    
    def __unicode__(self):
        return self.title
    
    class Meta:
        verbose_name = u'текст'
        verbose_name_plural = u'тексты'


class Ngramm(models.Model):
    n_gramm = models.CharField(db_index=True, verbose_name=u'N-грамма')
    text = models.ManyToManyField(Text, verbose_name=u'Текст')
    
    def __unicode__(self):
        return self.n_gramm
    
    class Meta:
        verbose_name = u'n-грамма'
        verbose_name_plural = u'n-граммы'


class Word(models.Model):
    word = models.CharField(db_index=True, verbose_name=u'Слово')
    probability = models.FloatField(default=0.0, verbose_name=u'Вероятность слова в тексте')
    n_gramm = models.ManyToManyField(Ngramm, verbose_name=u'N-грамма')
    
    def __unicode__(self):
        return self.word
    
    class Meta:
        verbose_name = u'слово'
        verbose_name_plural = u'слова'


class Significant(models.Model):
    significant = models.ManyToManyField('self', verbose_name=u'Сигнификаты')
    article = models.TextField(verbose_name=u'Словарная статья')
    
    class Meta:
        verbose_name = u'сигнификат'
        verbose_name_plural = u'сигнификаты'


class Triangle(models.Model):
    word = models.ForeignKey(Word, verbose_name=u'Слово')
    significant = models.ForeignKey(Significant, verbose_name=u'Сигнификат')
    weight = models.FloatField(default=0.5, verbose_name=u'Вес')
    
    class Meta:
        verbose_name = u'треугольник'
        verbose_name_plural = u'треугольники'


class Relation(models.Model):
    orientation = models.CharField(max_length=2, choices=ORIENTATION_CHOICES, verbose_name=u'Направление связи')
    significant1 = models.ForeignKey(Significant, verbose_name=u'Первый сигнификат')
    significant2 = models.ForeignKey(Significant, verbose_name=u'Второй сигнификат')
    weight = models.FloatField(default=0.0, verbose_name=u'Вес')
    
    class Meta:
        verbose_name = u'отношение'
        verbose_name_plural = u'отношения'
        
        
def create_table(cls):
    from django.db import connection
    from django.core.management.color import no_style
    
    sql, references = connection.creation.sql_create_model(cls, no_style())
    cursor = connection.cursor()
    for q in sql:
        try:
            cursor.execute(q)
        except:
            pass
