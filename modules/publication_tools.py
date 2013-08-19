#!/usr/bin/env python
# coding: utf8
from gluon import *

def check_citation(row):
    '''
    Checks that it is possible to generate a citation (at least one author and a year)
    '''
    return (len(row.author_list) > 1 and row.publication_year != None)

def make_citation(row):
    '''
    Generates a label resembling a text citation
    '''
    authors = row.author_list.split(';')
    if len(authors)==1: #single author
        author = authors[0].strip()
        return "{0} ({1})".format(author,row.publication_year)
    elif len(authors)==2:
        author1 = authors[0].strip()
        author2 = authors[1].strip()
        return "{0} and {1} ({2})".format(author1,author2,row.publication_year)
    else:
        author = authors[0].strip()
        return "{0} et al. ({1})".format(author,row.publication_year)
        
def issues_list(pub,db):
    '''
    Looks for problems with a publication and returns a list of strings identifying these problems
    '''
    result = []
    if not check_citation(pub):
       result.append("No Citation")
    ct = db.publication_curation
    if not (pub.curation_status):
        rows = db(ct.status == pub.dispensation).select()
        if rows:
            status_id = rows[0].id
            db(db.publication.id == pub.id).update(curation_status = status_id)
        elif (pub.dispensation == 'Downloaded'):
            status_id = db(ct.status == 'Have PDF').select()[0].id
            db(db.publication.id == pub.id).update(curation_status = status_id)
        else:    
            result.append("Curation status %s could not be auto-updated" % pub.dispensation)
    return result
