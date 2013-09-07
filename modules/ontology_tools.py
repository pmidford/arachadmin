#!/usr/bin/env python
# coding: utf8
#from gluon import *  #temporary, until we're ready to integrate
from urllib2 import urlopen
from lxml import etree

## This module is used to load owl format ontologies.  There should probably be a class for returned ontology information, but a dict might suffice


RDF_PREFIX = "{http://www.w3.org/1999/02/22-rdf-syntax-ns#}"
RDFS_PREFIX = "{http://www.w3.org/2000/01/rdf-schema#}"
OWL_PREFIX = "{http://www.w3.org/2002/07/owl#}"
OBO_PURL_PREFIX = "http://purl.obolibrary.org/obo/"

OWL_SUFFIX = ".owl"

RDF_RESOURCE = RDF_PREFIX + 'resource'
RDF_ABOUT = RDF_PREFIX + 'about'

RDFS_LABEL = RDFS_PREFIX + 'label'

OWL_CLASS = OWL_PREFIX + 'Class'
OWL_EQUIVALENTCLASS = OWL_PREFIX + 'equivalentClass'


class ClassTarget(object):
    def __init__(self):
        self.text = []
        self.class_list = []
        self.containerclass = None
    def start(self, tag, attrib):
        self.is_class = False
        self.is_label = False
        self.has_parent = False
        self.is_equivalent_class = False
        self.is_class_comment = False
        if tag == OWL_CLASS:
            self.is_class = True
            if attrib:
                if attrib[RDF_ABOUT]:
                    self.containerclass = {'about': attrib[RDF_ABOUT]}
        elif tag == OWL_EQUIVALENTCLASS:
            self.is_equivalent_class = True
        elif self.containerclass:
            if tag.endswith('label'):
                self.is_label = True
            elif tag.endswith('subClassOf'):
                self.containerclass['parent'] = attrib[RDF_RESOURCE]
                self.has_parent = True
            elif tag.endswith('IAO_0000115'):
                self.is_class_comment = True
    def end(self, tag):
        if tag == OWL_CLASS:
            if not self.is_equivalent_class:
                self.class_list.append(self.containerclass)
                self.containerclass = None
                self.is_class = False
        elif tag == OWL_EQUIVALENTCLASS:
            self.is_equivalent_class = False
        self.is_label = False
        self.has_parent = False
        self.is_class_comment = False
        pass
    def data(self, data):
        if self.is_label and self.containerclass:
            self.containerclass['label'] = data
        elif self.is_class_comment and self.containerclass:
            com = ''
            if 'class_comment' in self.containerclass:
                com = self.containerclass['class_comment']
            self.containerclass['class_comment'] = com + data
    def close(self):
        return self.class_list

def pplist(terms):
    import pprint
    pp = pprint.PrettyPrinter(indent=2)
    for term in terms:
        pp.pprint(term)

def process_tree(ont_tree):
    for child in ont_tree.getroot():
        print child.tag
    return ont_tree

ARACHNID_NODE = u'http://purl.obolibrary.org/obo/NCBITaxon_6854'

def build_ontology_tree(terms):
    import pprint
    pp = pprint.PrettyPrinter(indent=2)
    roots = []
    tree_dict = dict()
    parent_dict = dict()
    for term in terms:
        if term:
            if 'about' in term:
                tree_dict[term['about']] = term
            if 'parent' in term:
                tp = term['parent']
                if tp in parent_dict and parent_dict[tp] != None:
                   t1 = parent_dict[tp]
                   baz = t1.append(term)
                   parent_dict[tp] = t1
                else:
                   parent_dict[tp] = [term]
            else:
                roots.append(term)
    final_dict = dict()
    children = [tree_dict[ARACHNID_NODE]]
    while (children):
        child = children.pop(0)
        if 'about' in child:
            final_dict[child['about']] = child
        if child['about'] in parent_dict:
            newchildren = parent_dict[child['about']]
            children.extend(newchildren)
    print "added %d children of arachnid node" % len(final_dict)

def load_from_obo(ontology_name, processor):
    ontology_source = urlopen(OBO_PURL_PREFIX+ontology_name+OWL_SUFFIX)
    parser = etree.XMLParser(target = ClassTarget())
    results = etree.parse(ontology_source, parser)
    processor(results)

def demo():
    load_from_obo('ncbitaxon',build_ontology_tree)
