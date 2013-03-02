# coding: utf8
# try something like

def index():
    publications = db().select(db.publication.ALL, orderby=db.publication.id)
    return dict(publications=publications)

def list():
    publications = db().select(db.publication.ALL, orderby=db.publication.id)
    return dict(publications=publications)

def show():
    publication = db.publication(request.args(0,cast=int)) or redirect(URL('index'))
    form = SQLFORM(db.publication)
    return dict(publication=publication)
    
def enter():
    publication = db.publication(request.args(0,cast=int)) or redirect(URL('index'))
    form = SQLFORM(db.publication,publication)
    if form.process().accepted:
        response.flash = 'publication table modified'
    elif form.errors:
        response.false = 'errors in submission'
    return dict(form=form)
