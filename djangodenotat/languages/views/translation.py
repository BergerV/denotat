# -*- coding: utf-8 -*-
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render_to_response, get_list_or_404
from django.http import HttpResponseRedirect, QueryDict, HttpResponse
from django.template import RequestContext
from djangodenotat.languages.models import *
from djangodenotat.test.text_parser import make_string, split_by_sentences, make_final_string, split_n_gramm, encode_phrase
import json
from django.views.decorators.csrf import csrf_protect
import datetime
import time
from django.db.models import Max, Sum
from math import *
from itertools import permutations
from django.db import connection, transaction
from random import randrange, randint

def index(request, template_name="index.html"):
    languages = Language.objects.all()
    return render_to_response(template_name, locals(), 
        context_instance=RequestContext(request))                               

@csrf_protect
def trans(request):   
    if request.is_ajax():
        mimetype = 'application/javascript'
        postdata = request.POST
        msg = postdata['msg']
        langin = Language.objects.get(id = postdata['langin'])      
        langout = Language.objects.get(id = postdata['langout'])  
        #ПРОВЕРКА НА НАЛИЧИЕ КОМБИНАЦИЙ В СЛОВАРЕ
        change = False
        if not Translation.objects.filter(lang_orig = langin, lang_trans = langout).exists():
            print 'change langs'        
            change = True 
        #МАГИЯ СТАТИСТИЧЕСКОГО ПЕРЕВОДА#----#НАЧАЛО#        
        trans = translating(msg, langin, langout, change)
        #МАГИЯ СТАТИСТИЧЕСКОГО ПЕРЕВОДА#----#КОНЕЦ#
        js={"trans":trans}
        data= json.dumps(js)
        return HttpResponse(data,mimetype)
    else:
        return HttpResponse(status=400) 

def language_model(word, seq, lang, size):
    phrase = make_string([seq, word])        
    try:
        phrase_freq = Ngramm.objects.get(n_gramm = phrase, lang = lang).frequence
    except:
        phrase_freq = 0        
                
    #print seq
    try:
        seq_freq = Ngramm.objects.filter(n_gramm__istartswith = seq, lang = lang, n = size).aggregate(Sum('frequence'))
    except:    
        seq_freq = 0            
    #seq_freq = Ngramm.objects.get(n_gramm = seq, lang = lang)    
    V = Ngramm.objects.filter(n = size, lang = lang).count()    
    
    #print V
    p = float(1 + phrase_freq) / (seq_freq + V)    
    return p
    
#P(lm) новой гипотезы должна быть > предыдущей. соответственно perplexity должна быть меньше
    
def n_gramm_estimation(n_gramm, lang, size):          
    return language_model(make_string([n_gramm[size-1]]), make_string(n_gramm[0:size-1]), lang, size)
        
def uncertainty(orig, langin, trans, langout, change):    
    #print 'UNCERTAINTY'
    t = make_string(trans)    
    words = split_n_gramm(t)  
    #print words   
    sum_entropy = 0.0
    i = 0
    n = 5    
    while i < len(words):
        try:
            if i+n < len(words):
                sum_entropy += log(n_gramm_estimation(words[i:i+n], langout, n),2)
            else:
                sum_entropy += log(n_gramm_estimation(words[i:len(words)], langout, len(words)-i),2)
            i += n
        except:
            sum_entropy += -99999    
                   
    sum_max_prob = 0.0
    e_log = sum_entropy
    #print 'Entropy = ', sum_entropy     
    for (i, n_gramm) in enumerate(trans):
        try:
            t_gramm = Ngramm.objects.get(n_gramm = n_gramm, lang = langout)            
            o_gramm = Ngramm.objects.get(n_gramm = orig[i], lang = langout)    
            if change:                                
                sum_max_prob += log(Translation.objects.get(orig = n_gramm, lang_orig = langout, trans = orig[i], lang_trans = langin).probability, 2)       
            else:
                sum_max_prob += log(Translation.objects.get(orig = orig[i], lang_orig = langin, trans = n_gramm, lang_trans = langout).probability, 2)                   
        except:
            #sum_frequence = -99999   
            sum_max_prob += -99999      
#    try:
#        e_log = log(sum_entropy, 2)        
#    except:
#        e_log = -99999
    power = -1*(e_log + sum_max_prob/len(trans))        
    #print power
    if power > 10:
        #print 'a ', power
        return power
    #print 'b ',power    
    return pow(2, power)

def cross_entropy(text, langout, size):
    sum = 0.0    
    text = make_string(text)
    words = split_n_gramm(text)
    #разбиваем на н-граммы высшего порядка
    #words = join_by_n(text, size)      
    i = 0    
    while i < len(words):
        try:
            if i+size < len(words):
                sum += log(n_gramm_estimation(words[i:i+size], langout, size), 2)
            else:
                sum += log(n_gramm_estimation(words[i:len(words)], langout, len(words)-i), 2)               
        except:        
            sum += -99999    
        i += size
                       
    return (sum/len(words))        
    
def perplexity(text, lang, size):
    e = cross_entropy(text, lang, size)        
    try:
        return pow(2, (-1*e))
    except:
        return -1*e
       
def simple_translation(list_ngramm, langin, langout, change):    
    t = time.time()
    results = []
    for ngramm in list_ngramm:
        tmp = try_to_translate(ngramm, langin, langout, change)
        if tmp['trans'] == False:
            results.append(tmp['orig'])
        else:
            results.append(tmp['trans'])
        
    #print 'FINISH', results, time.time() - t
    return results    

           
def try_to_translate(ngramm, langin, langout, change):        
    t = time.time()    
    #print ngramm.encode('utf8')
    cursor = connection.cursor()
    if change:
        try:       
            cursor.execute("SELECT distinct languages_translation.probability FROM languages_translation WHERE languages_translation.lang_orig_id = %d AND languages_translation.lang_trans_id = %d AND languages_translation.trans = \'%s\' order by probability desc" % (langout.id, langin.id, ngramm.encode('utf8')))
            max_prob = cursor.fetchone()[0]   
        
            cursor.execute("SELECT languages_translation.orig FROM languages_translation WHERE languages_translation.lang_orig_id = %d AND languages_translation.lang_trans_id = %d AND languages_translation.trans = \'%s\' AND languages_translation.probability = %10.10f" % (langout.id, langin.id, ngramm.encode('utf8'), max_prob))           
            trans = cursor.fetchone()[0]                                             
            t = time.time() - t 
            #print 'rev FINISH TRANS-TRY', trans, t                        
            cursor.close()
            return {'orig':ngramm, 'trans':trans} 
        except:           
            #print 'rev FINISH LOSE'   
            cursor.close()
            return {'orig':ngramm, 'trans':False}   
    else:
        try:
            cursor.execute("SELECT distinct languages_translation.probability FROM languages_translation WHERE languages_translation.lang_orig_id = %d AND languages_translation.lang_trans_id = %d AND languages_translation.orig = \'%s\' order by probability desc" % (langin.id, langout.id, ngramm.encode('utf8')))
            max_prob = cursor.fetchone()[0]                        
                
            #print (time.time() - t ), max_prob                            
            cursor.execute("SELECT languages_translation.trans FROM languages_translation WHERE languages_translation.lang_orig_id = %d AND languages_translation.lang_trans_id = %d AND languages_translation.orig = \'%s\' AND languages_translation.probability = %10.10f" % (langin.id, langout.id, ngramm.encode('utf8'), max_prob))           
            
            trans = cursor.fetchone()[0]                                   
            
            t = time.time() - t 
            #print 'FINISH TRANS-TRY', trans, t            
            cursor.close()
            return {'orig':ngramm, 'trans':trans} 
        except:               
            #print 'FINISH LOSE'   
            cursor.close()
            return {'orig':ngramm, 'trans':False}                      
     

def spec_split(sp):
    v1 = [ make_string(sp[0:len(sp)-1]), sp[len(sp)-1] ]
    v2 = [ sp[0], make_string(sp[1:len(sp)]) ]
    return [v1, v2]
  
def join_by_n(words,n):
    tmp = []            
    i = 0
    while i < len(words):
        if i+n < len(words):
            tmp.append(make_string(words[i:i+n]))
        else:
            tmp.append(make_string(words[i:len(words)]))
        i += 1 #n
    return tmp        

def get_all_joins(text):
    res = []
    i = 0
    while i < len(text):
        for j in [4,3,2,1]:
            for per in permutations(text[i:i+j+1]):
                ngramm_tmp = ' '.join(per)
                res_text = text[0:i] + [ngramm_tmp] + text[i+j+1:len(text)] 
                res.add(res_text)                        
    return res    
    
def SWAP(orig, trans, langin, langout, change, un):
    distance = 0
    segment = 5 
    i = 0   
    ok = False    
    while i < len(trans):            
        ok = False 
        for s1 in range(1,segment+1):            
            for s2 in range(1,segment+1):
                #print s1, s2
                for d in range(0,distance+1):   
                    t_hypo = trans[0:i]+trans[i+s1+d:i+s1+s2+d]+trans[i+s1:i+s1+d]+trans[i:i+s1]+trans[i+s1+s2+d:len(trans)]
                    o_hypo =  orig[0:i]+ orig[i+s1+d:i+s1+s2+d]+ orig[i+s1:i+s1+d]+ orig[i:i+s1]+ orig[i+s1+s2+d:len(orig)]                    
                    un_new = uncertainty(o_hypo, langin, t_hypo, langout, change)
                    if un_new < un:
                        print 't: ', t_hypo, 'o: ', o_hypo
                        orig = o_hypo
                        trans = t_hypo
                        un = un_new 
                        ok = True
                        break
                if ok == True:        
                    break
            if ok == True:        
                break        
        i += 1                

    return {'orig': orig, 'trans': trans, 'un':un}        
    
def SWAP_P(orig, trans, langin, langout, change, pp):
    print 'SWAP'
    distance = 0
    segment = 5 
    i = 0   
    ok = False    
    while i < len(trans):            
        ok = False 
        for s1 in range(1,segment+1):            
            for s2 in range(1,segment+1):
                #print s1, s2
                for d in range(0,distance+1):   
                    t_hypo = trans[0:i]+trans[i+s1+d:i+s1+s2+d]+trans[i+s1:i+s1+d]+trans[i:i+s1]+trans[i+s1+s2+d:len(trans)]
                    o_hypo =  orig[0:i]+ orig[i+s1+d:i+s1+s2+d]+ orig[i+s1:i+s1+d]+ orig[i:i+s1]+ orig[i+s1+s2+d:len(orig)]                    
                    new_pp = perplexity(t_hypo, langout, 5)                        
                    if new_pp <= pp:                        
                        orig = o_hypo
                        trans = t_hypo
                        pp = new_pp
                        #print 'HYPO: ', make_string(trans), ' PP: ', new_pp
                        ok = True
                        break
                if ok == True:        
                    break
            if ok == True:        
                break        
        i += 1                

    return {'orig': orig, 'trans': trans, 'pp':pp}       
   
def CHANGE10(text, trans, langin, langout, change):
    #print 'CHANGE', text, trans
    cursor = connection.cursor()
    if change:
        try:
            #prob = Translation.objects.get(orig = trans, lang_orig = langout, trans = text, lang_trans = langin).probability
            cursor.execute("SELECT languages_translation.trans FROM languages_translation WHERE languages_translation.lang_orig_id = %d AND languages_translation.lang_trans_id = %d AND languages_translation.orig = \'%s\' AND NOT languages_translation.trans = \'%s\' order by probability desc LIMIT 10" % (langout.id, langin.id, trans.encode('utf8'), text.encode('utf8')))     
            res = cursor.fetchall()            
            #new_text = cursor.fetchone()[0]         
        except:
            print 'NO CHANGE'
            return {'orig':text, 'top_ten': []}             
    else:
        try:
            #prob = Translation.objects.get(orig = text, lang_orig = langin, trans = trans, lang_trans = langout).probability                
            cursor.execute("SELECT languages_translation.trans FROM languages_translation WHERE languages_translation.lang_orig_id = %d AND languages_translation.lang_trans_id = %d AND languages_translation.orig = \'%s\' AND NOT languages_translation.trans = \'%s\' order by probability desc LIMIT 10" % (langin.id, langout.id, text.encode('utf8'), trans.encode('utf8')))     
            res = cursor.fetchall()
            #new_text = cursor.fetchone()[0]                     
        except:
            print 'NO CHANGE'
            return {'orig':text, 'top_ten': []}
    
    cursor.close()    
    return {'orig':text, 'top_ten':res} 

def CHANGE(words, trans, langin, langout, change, un):
    i = 0
    j = 0
    n = len(words)    
    #получаем все комбинации для change    
    #while i <= n*n:
        #создаем гипотезу hypo
    for (j, word) in enumerate(words):
        #print j            
        changes = CHANGE10(word, trans[j], langin, langout, change)['top_ten']   
        changes = [item for sublist in changes for item in sublist]            
        for c in changes:
            hypo = trans[0:j] + [c] + trans[j+1:len(trans)]              
            #new_pp = perplexity(trans, langout, 5)
            un_new = uncertainty(words, langin, hypo, langout, change)           
            if un_new < un: 
                trans = hypo
                un = un_new
                print 'HYPO: ', make_string(hypo), ' UNS: ', un_new  
                break                
            else:
                i += 1    
    return {'orig':words,'trans':trans, 'un':un}      

def CHANGE_P(words, trans, langin, langout, change, pp):    
    print 'CHANGE'
    j = 0
    n = len(words)    
    #получаем все комбинации для change        
    #создаем гипотезу hypo
    for (j, word) in enumerate(words):
        #print j            
        changes = CHANGE10(word, trans[j], langin, langout, change)['top_ten']   
        changes = [item for sublist in changes for item in sublist]            
        for c in changes:
            hypo = trans[0:j] + [c] + trans[j+1:len(trans)]  
            new_pp = perplexity(hypo, langout, 5)       
            if new_pp <= pp: 
                trans = hypo
                pp = new_pp
                #print 'HYPO: ', make_string(hypo), ' PP: ', new_pp
                break                                      
    return {'orig':words,'trans':trans, 'pp':pp}           
    
def JOIN(text, trans, langin, langout, change, un):
    i = 0
    j = 0            
    while i < len(trans):
        try:           
            #print 'orig: ', text[i+1], 'trans:', trans[i]
            if change:                                
                prob = Translation.objects.get(orig = trans[i], lang_orig = langout, trans = text[i+1], lang_trans = langin).probability
            else:
                prob = Translation.objects.get(orig = text[i+1], lang_orig = langin, trans = trans[i], lang_trans = langout).probability
            #print 'ok'    
        except:
            prob = 0.0
            #print 'fail'
            
        if prob > 0.0:
            ngramm = make_string([text[i], text[i+1]])                        
            res_text = text[0:i] + [ngramm] + text[i+2:len(text)]            
            res_trans = trans[0:i] + [trans[i]] + trans[i+2:len(trans)]            
            un_new = uncertainty(res_text, langin, res_trans, langout, change)            
            if un_new < un:
                text = res_text
                trans = res_trans
                un = un_new     
                print 'HYPO: ', make_string(trans), ' PP: ', un                
                
        i += 1            
    return {'orig':text,'trans':trans, 'un':un}        
    
def JOIN_P(text, trans, langin, langout, change, pp):
    print 'JOIN'
    i = 0
    j = 0            
    while i < len(trans):
        try:           
            #print 'orig: ', text[i+1], 'trans:', trans[i]
            if change:                                
                prob = Translation.objects.get(orig = trans[i], lang_orig = langout, trans = text[i+1], lang_trans = langin).probability
            else:
                prob = Translation.objects.get(orig = text[i+1], lang_orig = langin, trans = trans[i], lang_trans = langout).probability
            #print 'ok'    
        except:
            prob = 0.0
            #print 'fail'
            
        if prob > 0.0:
            ngramm = make_string([text[i], text[i+1]])                        
            res_text = text[0:i] + [ngramm] + text[i+2:len(text)]            
            res_trans = trans[0:i] + [trans[i]] + trans[i+2:len(trans)]          
            new_pp = perplexity(res_trans, langout, 5)             
            #print 'HYPO: ', make_string(res_trans), ' PP: ', new_pp            
            if new_pp <= pp:
                text = res_text
                trans = res_trans
                pp = new_pp
                #print 'HYPO: ', make_string(trans), ' PP: ', new_pp
                
        i += 1            
    return {'orig':text,'trans':trans, 'pp':pp}       

def random_improve(text, trans, langin, langout, change, pp):
    #рандом
    n = (randint(1,100000) % 3) + 1 
    if n == 1:
        res = CHANGE_P(text, trans, langin, langout, change, pp)
        trans = res['trans']
        pp    = res['pp']           
    elif n == 2:                
        pair = SWAP_P(text, trans, langin, langout, change, pp)
        text  = pair['orig']    
        trans = pair['trans']           
        pp    = pair['pp']
    elif n == 3:
        pair  = JOIN_P(text, trans, langin, langout, change, pp)
        text  = pair['orig']    
        trans = pair['trans']
        pp    = pair['pp']        
        
    return {'orig':text,'trans':trans, 'pp':pp}    
    
def improve_n(n, text, trans, langin, langout, change, pp):
   
    if n == 2:
        res = CHANGE_P(text, trans, langin, langout, change, pp)
        trans = res['trans']
        pp    = res['pp']           
    elif n == 3:                
        pair = SWAP_P(text, trans, langin, langout, change, pp)
        text  = pair['orig']    
        trans = pair['trans']           
        pp    = pair['pp']
    elif n == 1:
        pair  = JOIN_P(text, trans, langin, langout, change, pp)
        text  = pair['orig']    
        trans = pair['trans']
        pp    = pair['pp']        
        
    return {'orig':text,'trans':trans, 'pp':pp}      

    
def improve(text, trans, langin, langout, change, pp):
    #рандом от 1 до 9
    n = (randint(1,100000) % 6) + 1 
    if n == 1:
        res = CHANGE_P(text, trans, langin, langout, change, pp)
        trans = res['trans']
        pp    = res['pp']
        
        pair  = JOIN_P(text, trans, langin, langout, change, pp)
        text  = pair['orig']    
        trans = pair['trans']
        pp    = pair['pp']        
    elif n == 2:
        res = CHANGE_P(text, trans, langin, langout, change, pp)
        trans = res['trans']
        pp    = res['pp']        
        
        pair = SWAP_P(text, trans, langin, langout, change, pp)
        text  = pair['orig']    
        trans = pair['trans']           
        pp    = pair['pp']
    elif n == 3:
        pair  = JOIN_P(text, trans, langin, langout, change, pp)
        text  = pair['orig']    
        trans = pair['trans']
        pp    = pair['pp']        
        
        res = CHANGE_P(text, trans, langin, langout, change, pp)
        trans = res['trans']
        pp    = res['pp']                
    elif n == 4:
        pair  = JOIN_P(text, trans, langin, langout, change, pp)
        text  = pair['orig']    
        trans = pair['trans']
        pp    = pair['pp']        
        
        pair = SWAP_P(text, trans, langin, langout, change, pp)
        text  = pair['orig']    
        trans = pair['trans']           
        pp    = pair['pp']
    elif n == 5:
        pair = SWAP_P(text, trans, langin, langout, change, pp)
        text  = pair['orig']    
        trans = pair['trans']           
        pp    = pair['pp']
        
        pair  = JOIN_P(text, trans, langin, langout, change, pp)
        text  = pair['orig']    
        trans = pair['trans']
        pp    = pair['pp']        
    elif n == 6:
        pair = SWAP_P(text, trans, langin, langout, change, pp)
        text  = pair['orig']    
        trans = pair['trans']           
        pp    = pair['pp']
        
        res   = CHANGE_P(text, trans, langin, langout, change, pp)
        trans = res['trans']
        pp    = res['pp']      
    elif n == 7:
        res = CHANGE_P(text, trans, langin, langout, change, pp)
        trans = res['trans']
        pp    = res['pp']        
        
        res = CHANGE_P(text, trans, langin, langout, change, pp)
        trans = res['trans']
        pp    = res['pp']       
    elif n == 8:
        pair = SWAP_P(text, trans, langin, langout, change, pp)
        text  = pair['orig']    
        trans = pair['trans']           
        pp    = pair['pp']
        
        pair = SWAP_P(text, trans, langin, langout, change, pp)
        text  = pair['orig']    
        trans = pair['trans']           
        pp    = pair['pp']
    elif n == 9:       
        pair  = JOIN_P(text, trans, langin, langout, change, pp)
        text  = pair['orig']    
        trans = pair['trans']
        pp    = pair['pp']
        
        pair  = JOIN_P(text, trans, langin, langout, change, pp)
        text  = pair['orig']    
        trans = pair['trans']
        pp    = pair['pp']        
        
    return {'orig':text,'trans':trans, 'pp':pp}       
                
def translating(msg, langin, langout, change):
    print 'START TRANSLATION', datetime.datetime.now()
    t = time.time() 
    text = split_by_sentences(msg)
    result = []
    words = []
    for s in text:        
        words += encode_phrase(s)
                
    #вычисление прямого перевода
    trans = simple_translation(words, langin, langout, change)      
    #вычисление величины неопределенности для полученного перевода   
    un = uncertainty(words, langin, trans, langout, change)              
    un_old = un
    print 'TRANS', make_final_string(trans), 'uns', un
    pp = perplexity(trans, langout, 5)      
    
    
    i = 0
    j = 0    
    k = 1
    reject = True
    n = len(words)    
    ok = True
    #получаем все комбинации для change    
    while i<100:
    #создаем гипотезу hypo
    #print i        
        if not reject:
            i = 0
            k = 1
        j = 0
        print k
        pair = improve(words, trans, langin, langout, change, pp)
        tmp_words = pair['orig']    
        tmp_trans = pair['trans']           
        pp_new = pair['pp']
        
        for j in range(1,4):
            pair = improve_n(j, tmp_words, tmp_trans, langin, langout, change, pp_new)
            tmp2_words = pair['orig']    
            tmp2_trans = pair['trans']                       
            pp_new2 = pair['pp']
                          
            un_new = uncertainty(tmp2_words, langin, tmp2_trans, langout, change)                      
            if un - un_new >= 0.001:
                un = un_new    
                words = tmp2_words
                trans = tmp2_trans
                pp = pp_new2            
                print 'HYPO: ', make_string(trans), ' PP: ', pp                
                reject = False
                break
            else:             
                reject = True            
                i+=1                                  
        if j == 3:
            k += 1
            if k > 9:
                break
            
    print 'TRANS', make_final_string(trans), 'uns-old', un_old, 'uns', un_new
    print i
    print 'END TRANSLATION', datetime.datetime.now()    
    t = time.time() - t 
    print 'TIME: ', t
    #result += pair['trans']
    #где-то тут мы производим детокенизацию    
    return make_final_string(trans)