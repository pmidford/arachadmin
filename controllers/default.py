# -*- coding: utf-8 -*-
# modified portions of this file are released under the MIT License, web2py portions were previously assigned to the public domain

# This controller is reponsible for the initial page shown when arachadmin starts up.

def index():
    result = dict()
    result['publications'] = db().select(db.publication.ALL, orderby=db.publication.author_list)
    result['assertions'] = db().select(db.assertion.ALL, orderby=db.assertion.id)
    result['taxa'] = db().select(db.taxon.ALL, orderby=db.taxon.id)
    #taxon_synonyms = db().select(db.taxon_synonym.ALL, orderby=db.taxon_synonym.id)
    result['behavior_terms'] = db().select(db.behavior_term.ALL, orderby=db.behavior_term.id)
    result['anatomy_terms'] = db().select(db.anatomy_term.ALL, orderby=db.anatomy_term.id)
    return result

def list_publications():
    publications = db().select(db.publication.ALL, orderby=db.publication.author_list)
    return dict(publications=publications)

def list_assertions():
    assertions = db().select(db.assertion.ALL, orderby=db.assertion.id)
    return dict(assertions=assertions)

def show():
    publication = db.publication(request.args(0,cast=int)) or redirect(URL('index'))
    form = SQLFORM(db.publication,publication)
    return dict(publication=publication)

def enter():
    publication = db.publication(request.args(0,cast=int)) or redirect(URL('index'))
    form = SQLFORM(db.publication,publication)
    if form.process().accepted:
        response.flash = 'publication table modified'
    elif form.errors:
        response.false = 'errors in submission'
    return dict(form=form)

def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    """
    return dict(form=auth())


def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()


def data():
    """
    http://..../[app]/default/data/tables
    http://..../[app]/default/data/create/[table]
    http://..../[app]/default/data/read/[table]/[id]
    http://..../[app]/default/data/update/[table]/[id]
    http://..../[app]/default/data/delete/[table]/[id]
    http://..../[app]/default/data/select/[table]
    http://..../[app]/default/data/search/[table]
    but URLs must be signed, i.e. linked with
      A('table',_href=URL('data/tables',user_signature=True))
    or with the signed load operator
      LOAD('default','data.load',args='tables',ajax=True,user_signature=True)
    """
    return dict(form=crud())
