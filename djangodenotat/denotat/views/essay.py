# -*- coding: utf-8 -*-

from django.http import HttpResponseRedirect, QueryDict, HttpResponse
import json
from django.views.decorators.csrf import csrf_protect
from djangodenotat.test import morph_analyze

@csrf_protect
def essay(request):
    if request.method == 'POST':
        mimetype = 'application/javascript'
        postfiles = request.FILES
        article = postfiles.get('article', False)

       # graph = analyze(article)

        result = 'result'

        js = {"result": result}
        data = json.dumps(js)
        return HttpResponse(data, mimetype)
    else:
        return HttpResponse(status=400)

def make_graphiz(graph):
    ok = True
    # morph_analyze.print_structures(graph)

    f = open('graph.gz.txt', 'w')
    f.write('digraph denotat {\n')
    f.write('size="10" \n')

    for s in graph:
        f.write('"'+s['parent'].normal_form.encode('utf-8')+'" [shape=box];\n')
        f.write('"'+s['child'].normal_form.encode('utf-8')+'" [shape=box];\n')
        f.write('"'+s['parent'].normal_form.encode('utf-8')+'" -> "' +
                s['child'].normal_form.encode('utf-8') +
                '" [ label = "'+s['verb'].normal_form.encode('utf-8')+'"];\n')

    f.write('}')
    f.close()

    inputfile = open("graph.gz.txt")
    unique = []
    for line in inputfile:
        line = line.strip()
        if line not in unique:
            unique.append(line)
    inputfile.close()
    for i in range(0, len(unique)):
        unique[i] += "\n"
    output = open("output.txt", "w")
    output.writelines(unique)
    output.close()

def analyze(text):
    graph = morph_analyze.analyze2(text)
    make_graphiz(graph)
