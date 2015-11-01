#!/usr/bin/python
# -*- coding: utf-8 -*-

import text_parser
from text_parser import morph

def connection(structures):
    #TODO прописать нормально эту функцию
    return structures


def find_root(structures):
    return {'parent': None, 'child': None, 'verb': None}


def concat_graphs(graph, structures):
    result = []
    root = find_root(structures)
    pos = find(graph, root)
    if pos:
        #TODO спуск от "корня" в эталоне и проверка на совпадения
        pass
    else:
        result = graph + structures
    return result


def find(graph, structure):
    for i, den in enumerate(graph):
        if structure['parent'] is not None:
            if den['child'].normal_form == structure['parent'].normal_form:
                return i
            if den['parent'].normal_form == structure['parent'].normal_form:
                return i
        elif den['child'] == structure['parent'] or den['parent'] == structure['parent']:
            return i
    return False


def find_in_graph(graph, structures):
    result = []
    for s in structures:
        result.append(s)
        for den in graph:
            if den['child'].normal_form == s['parent'].normal_form:
                result.append(den)
                if s['child'] is None and s['verb'] is None:
                    try:
                        result.remove(s)
                    except ValueError:
                        pass
            if den['parent'].normal_form == s['parent'].normal_form:
                pass
    return result


def search(graph, structure):
    result = []
    for den in graph:
        if den['parent'].normal_form == structure['parent'].normal_form:
            if den != None and structure != None:
                if den['verb'].normal_form == structure['verb'].normal_form and structure['verb'] is not None:
                    result.append(den)
                if den['child'].normal_form == structure['child'].normal_form and structure['child'] is not None:
                #TODO тут надо искать куски графа а не структуры
                    result.append(den)
    return result


def create_structures(graph, parent, children, verbs):
    print 'WE ARE HERE'
    structures = []
    if parent is not None and len(children) > 0 and len(verbs) > 0:
        for child in children:
            for verb in verbs:
                structures += [{'parent': parent, 'child': child, 'verb': verb}]
                print 'LOL'
    elif parent is not None and len(children) > 0:
        for child in children:
            """если оба найдены в эталонном графе то берем там глагол"""
            result = search(graph, {'parent': parent, 'child': child, 'verb': None})
            structures += result
    elif parent is not None and len(verbs) > 0:
        for verb in verbs:
            """если найдены варианты потомков в эталонном графе берем его к нам"""
            result = search(graph, {'parent': parent, 'child': None, 'verb': verb})
            structures += result
    elif parent is not None:
        structures += [{'parent': parent, 'child': None, 'verb': None}]
    return structures


def print_structures(structures):
    for s in structures:
        res = ''
        for val in s.itervalues():
            if val is not None:
                res += val.normal_form + ' '
        print res


def analyze(graph, text):
    structures = []
    sentences = text_parser.nltk_split_by_sentences(text)
    for sentence in sentences:
        words = text_parser.sentence_normal_form(sentence)
        print words
        verbs = []
        parent = None
        children = []
        for word in words:
            tag = morph.parse(word)[0].tag
            if tag.POS == 'NOUN':
                #проверяем найден ли родитель или падеж - должен быть именительный
                if parent is not None or tag.case != 'nomn':
                    print 'child:' + word, tag
                    #ура денотат-потомок!
                    children.append(word)
                else:
                    #ура денотат-родитель!
                    print 'parent:' + word, tag
                    parent = word
                #связка родитель-потомок
            elif tag.POS == 'VERB':
                print 'verb:' + word, tag
                verbs.append(morph.parse(word)[0].normal_form)
            if word == sentence[-1]:
                #создаем структуры
                new_structures = create_structures(graph, parent, children, verbs)
                structures += new_structures
    #объединяем структуры
    #structures = connection(structures)
    #заполняем лакуны
    print_structures(structures)
    structures = find_in_graph(graph, structures)
    #корректируем эталонный граф
    graph = concat_graphs(graph, structures)
    return graph


def analyze2(graph, text):
    structures = []
    graph = text_parser.graph_to_extra_form(graph)
    sentences = text_parser.nltk_split_by_sentences(text)
    for sentence in sentences:
        words = text_parser.sentence_normal_form_extra(sentence)
        verbs = []
        parent = None
        children = []
        for word in words:
            tag = word.tag
            if tag.POS == 'NOUN':
                #проверяем найден ли родитель или падеж - должен быть именительный
                if parent is not None or tag.case != 'nomn':
                    print 'child:' + word.normal_form, tag
                    #ура денотат-потомок!
                    children.append(word)
                else:
                    #ура денотат-родитель!
                    print 'parent:' + word.normal_form, tag
                    parent = word
                #связка родитель-потомок
            elif tag.POS == 'VERB':
                print 'verb:' + word.normal_form, tag
                verbs.append(word)
            elif tag.POS == 'PRTS':
                print 'verb:' + word.normal_form, tag
                verbs.append(word)
            elif tag.POS == 'PRCL':
                print 'verb:' + word.normal_form, tag
                verbs.append(word)
            # if word.word == sentence[-1]:
                #создаем структуры
        print 'NEW STRUCTURES'
        new_structures = create_structures(graph, parent, children, verbs)
        structures += new_structures
    #объединяем структуры
    #structures = connection(structures)
    #заполняем лакуны
    print_structures(structures)
    structures = find_in_graph(graph, structures)
    #корректируем эталонный граф
    graph = concat_graphs(graph, structures)
    return graph
