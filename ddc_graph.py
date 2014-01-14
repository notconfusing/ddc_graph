
# In[165]:

import xml.etree.ElementTree as ET
from collections import defaultdict
import networkx as nx
import matplotlib.pyplot as plt
import pyddc
import operator
import math
get_ipython().magic(u'pylab inline')


# Out[165]:

#     Populating the interactive namespace from numpy and matplotlib
# 

# We will be looking to populate a networkX DiGraph.

# In[2]:

G = nx.DiGraph()


# In[3]:

ET.register_namespace('marc', 'http://www.loc.gov/MARC21/slim')
tree = ET.parse('CLASS_23eng_marc_webdewey_20131020.xml')
root = tree.getroot()


# We're going to need these helper functions. 

# In[6]:

def valid_record(record):
    #is there a control field 008 whose byte 8 should be a
    valid = False
    for field in record:
            if field.tag == '{http://www.loc.gov/MARC21/slim}controlfield' and field.attrib['tag'] == '008':
                if field.text[8] == 'a':
                    valid = True
    return valid

def get_subfields(field, letters):
    ret_subfields = {letter: None for letter in letters}
    
    for subfield in field:
        if subfield.attrib['code'] in letters:
            ddc = pyddc.classification(subfield.text)
            if ddc.is_sane() and ddc.len() >= 3:
                ret_subfields[subfield.attrib['code']] = ddc
    return ret_subfields

def make_nodes(start_letter, end_letter):           
    k_nodes = list()
    #do we have a range?
    if start_letter and end_letter:
        try:
            k = pyddc.classification_range(start_letter, end_letter)
            k_nodes = k.ids()
        except AssertionError:
            #if the range is too large (more than ten) just take the first one 
            k_nodes = [start_letter.id]
        except ValueError:
            #not sure what to do with letters.
            raise ValueError
    #we might just have one
    elif start_letter and not end_letter:
        k_nodes = [start_letter.id]
    
    return k_nodes

def make_relationship(a_ddcs, b_ddcs, reltype):
    
    try:
    
        m_nodes = make_nodes(a_ddcs['a'], a_ddcs['c'])

        #maybe there's a better way to detect if we should be checking for e and f
        if b_ddcs.keys()[0] == 'e':
            n_nodes = make_nodes(b_ddcs['e'], b_ddcs['f'])
        else:
            n_nodes = make_nodes(b_ddcs['a'], b_ddcs['c'])
    
    except KeyError:
        print 'addc', a_ddcs, 
        print 'bddc', b_ddcs
    #put all the connections in our graph
    for m_node in m_nodes:
        for n_node in n_nodes:
            
            G.add_node(m_node)
            G.add_node(n_node)
            G.add_edge(m_node, n_node, rel=reltype)


# In[7]:

valid_records = filter(lambda record: valid_record(record), root)


# In[10]:

get_ipython().magic(u'pinfo valid_records')


# Interesting so every one of these records has a 153 field. I think that means that is it's canonical ddc.

# We have possibilites.
# 
# 1. Does 153 have 'e' or 'f'?
#     1. make_edge(reltionship = hiearchy, 153'ac', 153'ef')
# 2. Is there a 253_0?
#     1. make_edge(relationship = hiearchy, 253'ac', 153'ac')
# 3. Is there a 253_2?
# 
#     _there may be multiple $a fields_
#     1. make_edges(relationship = related, [253'a'], 153'ac')

# In[11]:

cases = defaultdict(int)

for record in valid_records:
    #our is out internal important bits of the record
    r = {num : None for num in ['153_base','153', '253_0', '253_2']}
    for field in record:
        if field.tag == '{http://www.loc.gov/MARC21/slim}datafield':
            num = field.attrib['tag']
            ind1 = field.attrib['ind1']                            
                            
            if num =='153': 
                r[num+'_base'] = get_subfields(field, ['a','c'])
                r[num] = get_subfields(field, ['e','f'])
            if num == '253':
                if ind1 == '0':
                    r[num +'_'+ ind1] = get_subfields(field, ['a','c'])
                if ind1 == '2':
                    r[num +'_'+ ind1] = get_subfields(field, ['a','c'])
    
    #we are expecting a gaurantee at this point that we have a 153 with a and maybe c    
    if r['153']['e']:
        cases[1] += 1
        make_relationship(r['153_base'], r['153'], reltype = 'hier')
    if r['253_0']:
        cases[2] += 1
        make_relationship(r['153_base'], r['253_0'], reltype = 'hier')
    if r['253_2']:
        cases[3] += 1
        make_relationship(r['153_base'], r['253_2'], reltype = 'related')

        
print cases


# Out[11]:

#     defaultdict(<type 'int'>, {1: 45480, 2: 5959, 3: 5918})
# 

# Ok so now we have __r__ as our main data

# make_nodes takes a start and end like 'a' and 'c' or 'e' and 'f' and even if the end is None returns the list of range beteween or just the list of length one of ids

# In[12]:

filter(lambda node: len(node) == 3 and node[1:3] == '00', G.nodes())


# Out[12]:

#     ['600', '800', '200', '400', '700', '900', '300', '500']

# Oddly I can't see why there should be no elements dhat have '000' or '100' as their parent

# In[14]:

nx.shortest_path(G,'075','005')


# Out[14]:

#     ['075', '616.8', '002', '368.6', '006', '005']

# In[31]:

G['075']


# Out[31]:

#     {'028': {'rel': 'hier'},
#      '070': {'rel': 'related'},
#      '071': {'rel': 'hier'},
#      '072': {'rel': 'hier'},
#      '073': {'rel': 'hier'},
#      '074': {'rel': 'hier'},
#      '075': {'rel': 'hier'},
#      '076': {'rel': 'hier'},
#      '077': {'rel': 'hier'},
#      '078': {'rel': 'hier'},
#      '079': {'rel': 'hier'},
#      '093': {'rel': 'hier'},
#      '094': {'rel': 'hier'},
#      '095': {'rel': 'hier'},
#      '096': {'rel': 'hier'},
#      '097': {'rel': 'hier'},
#      '098': {'rel': 'hier'},
#      '099': {'rel': 'hier'},
#      '280': {'rel': 'hier'},
#      '324.24': {'rel': 'hier'},
#      '324.25': {'rel': 'hier'},
#      '324.26': {'rel': 'hier'},
#      '324.27': {'rel': 'hier'},
#      '324.28': {'rel': 'hier'},
#      '324.29': {'rel': 'hier'},
#      '328.4': {'rel': 'hier'},
#      '328.5': {'rel': 'hier'},
#      '328.6': {'rel': 'hier'},
#      '328.7': {'rel': 'hier'},
#      '328.8': {'rel': 'hier'},
#      '328.9': {'rel': 'hier'},
#      '616.1': {'rel': 'hier'},
#      '616.2': {'rel': 'hier'},
#      '616.3': {'rel': 'hier'},
#      '616.4': {'rel': 'hier'},
#      '616.5': {'rel': 'hier'},
#      '616.6': {'rel': 'hier'},
#      '616.7': {'rel': 'hier'},
#      '616.8': {'rel': 'hier'},
#      '616.9': {'rel': 'hier'},
#      '617': {'rel': 'hier'},
#      '618.1': {'rel': 'hier'},
#      '618.2': {'rel': 'hier'},
#      '618.3': {'rel': 'hier'},
#      '618.4': {'rel': 'hier'},
#      '618.5': {'rel': 'hier'},
#      '618.6': {'rel': 'hier'},
#      '618.7': {'rel': 'hier'},
#      '618.8': {'rel': 'hier'},
#      '790.132': {'rel': 'related'}}

# In[90]:

def neighbors_n(G, root, n):
    E = nx.DiGraph()
    
    def n_tree(tree, n_remain):
        neighbors_dict = G[tree]
        
        for neighbor, relations in neighbors_dict.iteritems():
          E.add_edge(tree, neighbor, rel=relations['rel'])

        #you can use this map if you want to retain functional purity
        #map(lambda neigh_rel: E.add_edge(tree, neigh_rel[0], rel=neigh_rel[1]['rel']), neighbors_dict.iteritems() )

        neighbors = list(neighbors_dict.iterkeys())
        n_forest(neighbors, n_remain= (n_remain - 1))

    def n_forest(forest, n_remain):
        if n_remain <= 0:
            return
        else:
            map(lambda tree: n_tree(tree, n_remain=n_remain), forest)
        
    n_forest( [root] , n)
    
    return E


# In[107]:

nx.degree(E, '075')


# Out[107]:

#     51

# In[182]:

def draw_n_hops(G, root, n):
    E = neighbors_n(G, root, n)
    edge_rels = map(lambda edge_tup: edge_tup[2]['rel'], E.edges(data=True) )
    edge_colors = map(lambda edge: 'grey' if edge == 'hier' else 'green', edge_rels)
    
    max_node_size = max( map(lambda node: nx.degree(E, node), E.nodes()))
                             
    node_lognorms = map(lambda node: (math.log(nx.degree(E, node)) / math.log(max_node_size) ) , E.nodes() )
    node_sizes = map(lambda norm: norm * 1500, node_lognorms)    
    
    node_colors= node_lognorms
    
    pos=nx.graphviz_layout(E,prog="twopi",root=root)
                                            
    
    plt.figure(1,figsize=(20,20))
    nx.draw(E, pos=pos, node_size=node_sizes, node_color=node_colors, edge_color=edge_colors)


# In[185]:

draw_n_hops(G, '075', 2)


# Out[185]:

# image file:

# In[13]:

subgraphs = nx.connected_component_subgraphs(UG)
UG_big = subgraphs[0]


# In[21]:

mains = filter(lambda node: len(node) == 3 and node[1:3] == '00', UG_big.nodes())


# In[18]:

for main in mains:
    UG_big.add_edge('start',main, rel='hier')


# In[7]:

any(map(lambda n: n==4, map(lambda d: len(d), deplist)))


# Out[7]:

#     False
