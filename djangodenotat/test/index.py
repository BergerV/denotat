#!/usr/bin/python
# -*- coding: utf-8 -*-

import morph_analyze
import json

def make_graphiz(graph):
    ok = True
    #morph_analyze.print_structures(graph)

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

if __name__ == '__main__':
    text = json.load(open('text'))['text']
    reference = json.load(open('ref'))

    graph = reference
    graph = morph_analyze.analyze2(graph, text)

    make_graphiz(graph)
    print 'FINISH'
