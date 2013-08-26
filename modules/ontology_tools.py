#!/usr/bin/env python
# coding: utf8
#from gluon import *  #temporary, until we're ready to integrate
from urllib2 import urlopen
from lxml import etree

## This module is used to load owl format ontologies.  There should probably be a class for returned ontology information, but a dict might suffice

OBO_PURL_PREFIX = "http://purl.obolibrary.org/obo/"
OWL_SUFFIX = ".owl"

RDF_RESOURCE = '{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource'
RDF_ABOUT = '{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about'

class ontology(object):
    name_id = dict()
    name = ''
    def __init__(self,etree):
      name = "test"
      
class ClassTarget(object):
    def __init__(self):
        self.text = []
        self.class_list = []
        self.containerclass = None
    def start(self, tag, attrib):
        self.is_class = False
        self.is_label = False
        self.has_parent = False
        self.is_class_comment = False
        if tag.endswith('Class'):
            self.is_class = True
            if attrib:
                if attrib[RDF_ABOUT]:
                    self.containerclass = {'about': attrib[RDF_ABOUT]}
        elif self.containerclass:
            if tag.endswith('label'):
                self.is_label = True
            elif tag.endswith('subClassOf'):
                self.containerclass['parent'] = attrib[RDF_RESOURCE]
                self.has_parent = True
            elif tag.endswith('IAO_0000115'):
                self.is_class_comment = True
    def end(self, tag):
        if tag.endswith('Class'):
            self.class_list.append(self.containerclass)
            self.containerclass = None
        self.is_class = False
        self.is_label = False
        self.has_parent = False
        self.is_class_comment = False
        pass
    def data(self, data):
        if self.is_label and self.containerclass:
            self.containerclass['label'] = data
        elif self.is_class_comment and self.containerclass:
            self.containerclass['class_comment'] = data
    def close(self):
        return self.class_list

def load_from_obo(ontology_name):
    import pprint
    pp = pprint.PrettyPrinter(indent=2)
    ontology_source = urlopen(OBO_PURL_PREFIX+ontology_name+OWL_SUFFIX)
    parser = etree.XMLParser(target = ClassTarget())
    results = etree.parse(ontology_source, parser)  
    for result in results:
        pp.pprint(result)

def process_tree(ont_tree):
    for child in ont_tree.getroot():
        print child.tag
    return ont_tree
