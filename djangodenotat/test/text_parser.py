#!/usr/bin/python
# -*- coding: utf-8 -*-

import nltk
import pymorphy2
import re

morph = pymorphy2.MorphAnalyzer()

def split_into_ngramm(sentence, ngramm):
    try:
        tmp = unicode(sentence.strip(), "utf-8")
    except:
        tmp = sentence.strip()
    tmp = split_by_words_and_punctuation(tmp.lower())
    tmp = replace_numbers(tmp)
    tmp = replace_all_quotes(tmp)
    final = []
    for j in xrange(1, ngramm+1):
        for i in xrange(len(tmp)-j+1):
            final.append(make_string(tmp[i:j+i]))
    return final


def encode_phrase(phrase):
    try:
        tmp = unicode(phrase.strip(), "utf-8")
    except:
        tmp = phrase.strip()
    tmp = split_by_words_and_punctuation(tmp.lower())
    tmp = replace_numbers(tmp)
    tmp = replace_all_quotes(tmp)
    return tmp


def split_by_sentences(text):
    sentenceEnders = re.compile(r'''[.!?]['"]?\s{1,2}(?=[A-Z])''', re.UNICODE)
    sentenceList = sentenceEnders.split(text)
    return sentenceList


def nltk_split_by_sentences(text):
    pst = nltk.tokenize.PunktSentenceTokenizer()
    sentences = pst.sentences_from_text(text.lower())
    return sentences


def split_by_words(text):
    return re.findall(r'\w+', text)


def split_by_words_and_punctuation(text):
    try:
        text = unicode(text, "utf-8")
    except Exception as e:
        print e
    return re.findall(r"\w+(?:-\w+)+|[\w']+|[^\s\w]", text, re.UNICODE)


def split_n_gramm(text):
    return text.split()


#замена кавычек на токен <QUOTE>
def replace_all_quotes(text):
    res = []
    for s in text:
        s = re.sub(r'"', r'''<QUOTE>''', s)
        res.append(s)
    return res


def make_string(text):
    return ' '.join(text)


def make_final_string(text):
    tmp = re.sub(r'''<QUOTE>''', '"', ' '.join(text))
    tmp = re.sub(r'''\s+([,;:?.!\)\}\]])''', r'\1', tmp)
    return re.sub(r'''([\(\[\{])\s+''', r'\1', tmp)


#замена чисел на токен <NUM>
def replace_numbers(text):
    res = []
    for s in text:
        s = re.sub(r'\b\d+\b', "<NUM>", s)
        res.append(s)
    return res

#получения текста как списка токенов
def nltk_parse_to_tokens(paragraph):
    tokens = []
    #параграфы на предложения
    pst = nltk.tokenize.PunktSentenceTokenizer()
    sentences = pst.sentences_from_text(paragraph.lower())
    for sentence in sentences:
        #предложения на слова
        tokens += nltk.tokenize.WordPunctTokenizer().tokenize(sentence)
    return tokens


def sentence_normal_form(sentence):
    normal_words = []
    words = split_by_words_and_punctuation(sentence)
    for word in words:
        res = morph.parse(word)[0]
        if res.tag.POS != 'VERB':
            normal_words.append(res.normal_form)
        else:
            normal_words.append(word)
    return normal_words

def sentence_normal_form_extra(sentence):
    normal_words1 = []
    normal_words2 = []
    words = split_by_words_and_punctuation(sentence)
    for word in words:
        variants = morph.parse(word)
        res = {}
        for variant in variants:
            res.update({variant.tag.POS:variant})
        for form in ['NOUN','VERB','PRTS','PRCL','PREP']:
            try:
                x = res[form]
            except KeyError, e:
                pass
            finally:
                normal_words1.append(x)
        normal_words2.append(variants[0])
        print ">>>>>",len(normal_words1)
        print "<<<<<",len(normal_words2)
    return normal_words1

#граф в расширенную форму
def graph_to_extra_form(graph):
    for s in graph:
        s['parent'] = morph.parse(s['parent'])[0]
        s['verb'] = morph.parse(s['verb'])[0]
        s['child'] = morph.parse(s['child'])[0]
    return graph

#получения текста как списка токенов в нормальной форме
def get_normal_form(text):
    sentences = split_by_sentences(text)
    words = []
    for sentence in sentences:
        words += encode_phrase(sentence)
    normal_words = []
    for word in words:
        res = morph.parse(word)[0]
        if res.tag.POS != 'VERB':
            normal_words.append(res.normal_form)
        else:
            normal_words.append(word)
    return normal_words
