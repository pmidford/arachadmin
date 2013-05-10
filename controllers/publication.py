# coding: utf8
# try something like

def index():
    redirect(URL('list'))

def list():
    publications = db().select(db.publication.ALL, orderby=db.publication.id)
    return dict(publications=publications)

def show():
    publication = db.publication(request.args(0,cast=int)) or redirect(URL('list'))
    form = SQLFORM(db.publication)
    return dict(publication=publication)
    
def enter():
    if request.args(0):
        publication = db.publication(request.args(0,cast=int))
        form = SQLFORM(db.publication,publication)
    else:
        form = SQLFORM(db.publication)
    if form.process().accepted:
        response.flash = 'publication table modified'
    elif form.errors:
        response.false = 'errors in submission'
    return dict(form=form)
