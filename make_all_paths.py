# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <headingcell level=1>

# Dewey Decimal Classification as a Graph

# <markdowncell>

# We look at the DDC, from a graph theoretic approach. So each 
# 
# * *classification* is a *node*
# * *relations* between *classifications* - like *hiearchy* or *see also*, are *edges*
# * Then the distance beteween two nodes, are a classifications *relatedness*

# <codecell>

import xml.etree.ElementTree as ET
from collections import defaultdict
import networkx as nx
import matplotlib.pyplot as plt
import pyddc
import pymarc
import operator
import math
import json


# <codecell>
print 'loading xml'
completedb = pymarc.parse_xml_to_array(open('CLASS_23eng_marc_webdewey_20131020.xml'))
print 'loaded xml'
# <markdowncell>

# Our rules:
# 
# * only if leader byte 8 is 'a'
# * exclude spans,  recrods that have eithe \$c or \$y in 153
# * 253 ind 0  \$a "see reference"
# * 253 ind 2  \$a "class elsewhere"
#      * may be multiple 253s
# * 153 \$a to $e is "notational hiearchy"
# 
# 
# Later on tables:
# 
# * check for 008 6th byte is 'b' for table and 153 \$z exists
# * in 765 \$z is table num, \$s through \$t, relation will be "built from"

# <codecell>

graphs = defaultdict(nx.DiGraph)

for record in completedb:
    class_num = None
    table_num = None
    tabl_class_num = None
    
    for field in record.fields:
        
        #conditon 153 
        if field.tag == '153':
            y_z_subfields = field.get_subfields('y','z')
            
            #nontables
            if not y_z_subfields:
                a_subfields = field.get_subfields('a')
                a = a_subfields[0]
                class_num = a
                #checking to see if we have notational hiearchy:
                e_subfields = field.get_subfields('e')
                if e_subfields:
                    graphs['main'].add_edge(class_num, e_subfields[0], rel='notational_hiearchy')
            #tables
            '''
            else:
                z = field.get_subfields('z')
                y = field.get_subfields('y')
                
                if y and not z:
                    f['a']+=1
                    #print field
                if z and not y:
                    f['b']+=1
                    print unicode(field)
            '''
            
        #condition 253
        if field.tag == '253':
            
            if field.indicator1 == '0':
                y_z_subfields = field.get_subfields('y','z')
                if not y_z_subfields:
                    a_subfields = field.get_subfields('a')
                    if a_subfields:
                        if class_num:
                            graphs['main'].add_edge(class_num, a_subfields[0], rel='see_reference')
            
            if field.indicator1 == '2':
                y_z_subfields = field.get_subfields('y','z')
                if not y_z_subfields:
                    a_subfields = field.get_subfields('a')
                    if a_subfields:
                        if class_num:
                            graphs['main'].add_edge(class_num, a_subfields[0], rel='class_elsewhere')
                            
        if field.tag == '765':
            
                z = field.get_subfields('z')
                s = field.get_subfields('s')

                if z and s:
                    if len(z) == len(s):
                        if len(z) == 1:
                            if class_num:
                                graphs[z[0]].add_edge(class_num, s[0], rel='built_from')

# <codecell>

d = defaultdict(dict)

fileloc = open('~/data/all_ddc_paths','w')

print 'will save to: ', fileloc


G = graphs['main']
for m in G.nodes():
	print 'computing: ', m
	for n in G.nodes():
		if not m == n:
			d[m][n] = list(nx.all_simple_pathspaths(G, m, n))

print 'dumping'
json.dump(d, fileloc)
print 'done'
# <codecell>

