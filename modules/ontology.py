#!/usr/bin/env python
# coding: utf8
#from gluon import *  #temporary, until we're ready to integrate
from urllib2 import urlopen
from lxml import etree

## This module is used to load owl format ontologies.  There should probably be a class for returned ontology information, but a dict might suffice

OBO_PURL_PREFIX = "http://purl.obolibrary.org/obo/"
OWL_SUFFIX = ".owl"

class ontology(object):
    name_id = dict()
    name = ''
    def __init__(self,etree):
      name = "test"
      
      
def load_from_obo(ontology_name):
    ontology_url_str = OBO_PURL_PREFIX+ontology_name+OWL_SUFFIX
    ont_tree = etree.parse(ontology_url_str)
    if ont_tree:
        return process_tree(ont_tree)
    else:
        return None

def process_tree(ont_tree):
    for child in ont_tree.getroot():
        print child.tag
    return ont_tree
