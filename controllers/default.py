# -*- coding: utf-8 -*-
# modified portions of this file are released under the MIT License,
# web2py portions were previously assigned to the public domain


def index():
    """
    This function is reponsible for the initial (home) page shown
    when arachadmin starts up.
    """
    publist = db().select(db.publication.ALL, 
                          orderby=db.publication.author_list)
    claimslist = db().select(db.claim.ALL, orderby=db.claim.id)
    taxalist = db().select(db.taxon.ALL, orderby=db.taxon.id)
    return {'publications': publist,
            'claims': claimslist,
            'taxa': taxalist}


def list_publications():
    publications = db().select(db.publication.ALL,
                               orderby=db.publication.author_list)
    return {'publications': publications}


def list_claims():
    claims = db().select(
        db.claim.ALL,
        orderby=db.claim.id)
    return {'claims': claims}


def show():
    publication = (db.publication(request.args(0, cast=int)) or
                   redirect(URL('index')))
    form = SQLFORM(db.publication, publication)
    return {'publication': publication}


def enter():
    publication = (db.publication(request.args(0, cast=int)) or
                   redirect(URL('index')))
    form = SQLFORM(db.publication, publication)
    if form.process().accepted:
        response.flash = 'publication table modified'
    elif form.errors:
        response.flash = 'errors in submission'
    return {'form': form}


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
