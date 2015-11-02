# -*- coding: utf-8 -*-
from djangodenotat.languages.models import *
from djangodenotat.test.text_parser import split_into_ngramm, split_by_words_and_punctuation
from collections import defaultdict
from django.conf import settings
import json
import codecs
from djangodenotat.languages.views.translation import *
from math import *


@csrf_protect
def evaluation(request):   #bleu metric
    if request.is_ajax():
        mimetype = 'application/javascript'
        postdata = request.POST
        postfiles = request.FILES
        orig = postfiles['orig_name']
        ref = postfiles['trans_name']
        langin = Language.objects.get(id=postdata['langin'])
        langout = Language.objects.get(id=postdata['langout'])
        count = 0        
        score = 0.0  
        metric = 0.0       
        for (o, r) in zip(orig, ref):
            h = translating(o, langin, langout, False)            
            score += BLEU(h, r)
            count += 1
            print count, score
        
        metric = score / float(count)    
        print 'BLEU = ', metric
        js = {"bleu": metric}
        data = json.dumps(js)
        return HttpResponse(data, mimetype)

    else:
        return HttpResponse(status=400)

        
def BLEU(hyp, ref):
    # print 'BLEU'
    metric = 0.0
    hyp_list = split_by_words_and_punctuation(hyp.lower())
    ref_list = split_by_words_and_punctuation(ref.lower())   
    hyp_len = len(hyp_list)
    ref_len = len(ref_list)
    h_list = split_into_ngramm(hyp, 5)
    r_list = split_into_ngramm(ref, 5)
    
    if ref_len < hyp_len:
        Bp = 1
    else:
        Bp = exp(1-(float(hyp_len)/ref_len))    
    sum = 0.0
    N = 4
    for i in range(1, N+1):
        try:
            p = log(Pn(h_list, r_list, i), 2)        
        except:
            p = -99999
        sum += (p/float(N))

    metric = Bp*exp(sum)
    print 'BLEU =', metric
    return metric

    
def Pn(hyp, ref, size):
    p = 0.0
    count = 0
    equal = 0
    tmp = set(hyp) & set(ref)    
    u_hyp = set(hyp)
    for n_gramm in tmp:        
        if len(split_n_gramm(n_gramm)) == size:
            equal += 1        
    for n_gramm in hyp:        
        if len(split_n_gramm(n_gramm)) == size:
            count += 1
    try:            
        return float(equal)/count
    except:
        print 'division by zero!'
        return 0


def len_text(text):
    l = 0
    for s in text:
        l += len(split_by_words_and_punctuation(s.strip()))        
    return l


def bitext(orig, trans):
    for (o, t) in zip(orig, trans):        
        yield (split_into_ngramm(o, 5), split_into_ngramm(t, 5))


def normalize(table):
    for (ow, twtable) in table.iteritems():
        Z = sum(twtable.values())
        for tw in twtable:
            twtable[tw] = twtable[tw] / Z


@csrf_protect
def load2(request):   #составление списка n-грамм     
    if request.is_ajax():
        mimetype = 'application/javascript'
        postdata = request.POST
        postfiles = request.FILES
        orig = postfiles['orig_name']
        trans = postfiles['trans_name']
        langin = Language.objects.get(id=postdata['langin'])
        langout = Language.objects.get(id=postdata['langout'])

        #магия с обработкой параллельных текстов ---- НАЧАЛО   
        print 'START', datetime.datetime.now()
        table = defaultdict(lambda: defaultdict(float))  
        otable = defaultdict(float)
        ttable = defaultdict(float)
        text = bitext(orig, trans)
        len_o = len_text(orig)                
        len_t = len_text(trans)
        print len_o, len_t    
        
        print 'MAKING LIST OF UNIQUE N-GRAMMS', datetime.datetime.now()
        u_o = []
        u_t = []                
        
        for (o, t) in text:            
            for ow in o: 
                if ow not in u_o:                     
                    u_o.append(ow)
            for tw in t: 
                if tw not in u_t:                     
                    u_t.append(tw)
        text_unique = [u_o, u_t]             #список уникальных n-грамм

        print 'CALCULATING N-GRAMM FREQUENCE', datetime.datetime.now()
        for o in text_unique[0]:
            otable[ow] = 0
        for t in text_unique[1]:
            ttable[ow] = 0
                  
        for (o, t) in bitext(orig, trans):
            for ow in o: 
                otable[ow] += float(1)/len_o
            for tw in t: 
                ttable[tw] += float(1)/len_t

        print 'WRITE N-GRAMMS IN FILE', datetime.datetime.now()

        cursor = connection.cursor()
        filename = settings.PROJECT_PATH + '/ngramm.tmp'
        i = 0      
        f = codecs.open(filename, "w", "utf-8")                
        print 'OPEN FILE'
        for o in text_unique[0]:
            f.write('"%s",%s,%s,%.10f\n' % (o.replace('"', "'"), len(split_n_gramm(o)), langin.id, otable[o]))            
            i += 1
                        
            if i >= 900:
                i = 0
                f.close()
                cursor.execute('COPY languages_ngramm (n_gramm, n, lang_id, frequence) FROM \'%s\' DELIMITERS \',\' CSV' % filename)
                transaction.commit_unless_managed()                
                f = codecs.open(filename, "w", "utf-8") 

        f.close()                        
        cursor.execute('COPY languages_ngramm (n_gramm, n, lang_id, frequence) FROM \'%s\' DELIMITERS \',\' CSV' % filename)               
        transaction.commit_unless_managed()
                    
        i = 0      
        f = codecs.open(filename, "w", "utf-8")                
        for t in text_unique[1]:
            f.write('"%s",%s,%s,%.10f\n' % (t.replace('"', "'"), len(split_n_gramm(t)), langout.id, ttable[t]))                
            i += 1
                        
            if i >= 900:
                i = 0
                f.close()
                cursor.execute('COPY languages_ngramm (n_gramm, n, lang_id, frequence) FROM \'%s\' DELIMITERS \',\' CSV' % filename)               
                transaction.commit_unless_managed()
                f = codecs.open(filename, "w", "utf-8") 
                        
        f.close()
        cursor.execute('COPY languages_ngramm (n_gramm, n, lang_id, frequence) FROM \'%s\' DELIMITERS \',\' CSV' % filename)               
        transaction.commit_unless_managed()
        cursor.close()
        
        # магия с обработкой параллельных текстов ---- КОНЕЦ
        print 'END', datetime.datetime.now()
        
        return HttpResponse('',mimetype)
    else:
        return HttpResponse(status=400)


@csrf_protect
def load(request):        
    if request.is_ajax():
        mimetype = 'application/javascript'
        postdata = request.POST
        postfiles = request.FILES
        orig = postfiles['orig_name']
        trans = postfiles['trans_name']
        langin = Language.objects.get(id=postdata['langin'])
        langout = Language.objects.get(id=postdata['langout'])

        # магия с обработкой параллельных текстов ---- НАЧАЛО
        print 'START', datetime.datetime.now()
        table = defaultdict(lambda: defaultdict(float))  
        otable = defaultdict(float)
        ttable = defaultdict(float)
        text = bitext(orig, trans)
        len_o = len_text(orig)                
        len_t = len_text(trans)
        print len_o, len_t    
        
        print 'MAKING LIST OF UNIQUE N-GRAMMS', datetime.datetime.now()
        u_o = []
        u_t = []                
        
        for (o, t) in text:            
            for ow in o: 
                if ow not in u_o:                     
                    u_o.append(ow)
            for tw in t: 
                if tw not in u_t:                     
                    u_t.append(tw)
        text_unique = [u_o, u_t]             # список уникальных n-грамм

        print 'CALCULATING N-GRAMM FREQUENCE', datetime.datetime.now()
        for o in text_unique[0]:
            otable[ow] = 0
        for t in text_unique[1]:
            ttable[ow] = 0
                  
        for (o, t) in bitext(orig, trans):
            for ow in o: 
                otable[ow] += float(1)/len_o
            for tw in t: 
                ttable[tw] += float(1)/len_t
                
        print 'WRITE N-GRAMMS IN FILE', datetime.datetime.now()

        cursor = connection.cursor()
        filename = settings.PROJECT_PATH + '/ngramm.tmp'
        i = 0      
        f = codecs.open(filename, "w", "utf-8")                
        print 'OPEN FILE'
        for o in text_unique[0]:
            f.write('"%s",%s,%s,%.10f\n' % (o.replace('"', "'"), len(split_n_gramm(o)), langin.id, otable[o]))            
            i += 1
                        
            if i >= 900:
                i = 0
                f.close()
                cursor.execute('COPY languages_ngramm (n_gramm, n, lang_id, frequence) FROM \'%s\' DELIMITERS \',\' CSV' % filename)               
                transaction.commit_unless_managed()                
                f = codecs.open(filename, "w", "utf-8") 

        f.close()                        
        cursor.execute('COPY languages_ngramm (n_gramm, n, lang_id, frequence) FROM \'%s\' DELIMITERS \',\' CSV' % filename)               
        transaction.commit_unless_managed()
                    
        i = 0      
        f = codecs.open(filename, "w", "utf-8")                
        for t in text_unique[1]:
            f.write('"%s",%s,%s,%.10f\n' % (t.replace('"', "'"), len(split_n_gramm(t)), langout.id, ttable[t]))                
            i += 1
                        
            if i >= 900:
                i = 0
                f.close()
                cursor.execute('COPY languages_ngramm (n_gramm, n, lang_id, frequence) FROM \'%s\' DELIMITERS \',\' CSV' % filename)               
                transaction.commit_unless_managed()
                f = codecs.open(filename, "w", "utf-8") 
                        
        f.close()
        cursor.execute('COPY languages_ngramm (n_gramm, n, lang_id, frequence) FROM \'%s\' DELIMITERS \',\' CSV' % filename)               
        transaction.commit_unless_managed()
        cursor.close()
        
        for (o,t) in bitext(orig, trans):
            for ow in o: 
                for tw in t: 
                    table[ow][tw] = 0.5   
        
        n = 10

        for i in xrange(n):
            print 'iteration {'+str(i)+'}...', datetime.datetime.now()
            counts = defaultdict(float)
            total = defaultdict(float)
            # print 'E-step'
            for (o, t) in bitext(orig, trans):
                for ow in o:
                    stotal = sum(table[ow].values())
                    for tw in t:
                        c = table[ow][tw] / stotal
                        counts[(ow, tw)] += c
                        total[tw] += c          

            # print 'M-step'
            for (o, t) in bitext(orig, trans):
                for ow in o: 
                    for tw in t: 
                        table[ow][tw] = counts[(ow, tw)] / total[tw]

        print 'WRITE N-GRAMM TABLE IN FILE', datetime.datetime.now()

        cursor = connection.cursor()
        filename = settings.PROJECT_PATH + '/copy.tmp'
        i = 0      
        k = 0
        f = codecs.open(filename, "w", "utf-8") 
        for ow in table.iterkeys():
            for tw in table[ow].iterkeys():                
                probability = table[ow][tw]
                if probability > 0.0:
                    f.write('"%s",%s,"%s",%s,%.10f\n' % (ow, langin.id, tw, langout.id, probability))
                    i += 1
                        
                    if i >= 900:
                        i = 0                        
                        print 'iteration {'+str(k)+'}...', datetime.datetime.now()
                        k += 1
                        f.close()
                        cursor.execute('COPY languages_translation (orig, lang_orig_id, trans, lang_trans_id, probability) FROM \'%s\' DELIMITERS \',\' CSV' % filename)
                        transaction.commit_unless_managed()
                        f = codecs.open(filename, "w", "utf-8") 

        f.close()                        
        cursor.execute('COPY languages_translation (orig, lang_orig_id, trans, lang_trans_id, probability) FROM \'%s\' DELIMITERS \',\' CSV' % filename)
        transaction.commit_unless_managed()
        cursor.close()
        # магия с обработкой параллельных текстов ---- КОНЕЦ
        print 'END', datetime.datetime.now()
        
        return HttpResponse('', mimetype)
    else:
        return HttpResponse(status=400)
