# coding: utf8
# try something like
def index():
    redirect(URL('list'))
    
def list():
    taxa = db().select(db.taxon.ALL, orderby=db.taxon.id)
    return dict(taxa=taxa)
    
def show():
    taxa = db.taxon(request.args(0,cast=int)) or redirect(URL('list'))
    form = SQLFORM(db.taxon)
    return dict(taxa=taxa)
    
def enter():
    if request.args(0):
        taxon = db.taxon(request.args(0,cast=int))
        form = SQLFORM(db.taxon,taxon)
    else:
        form = SQLFORM(db.taxon)
    if form.process().accepted:
        response.flash = 'taxon table modified'
    elif form.errors:
        response.false = 'errors in submission'
    return dict(form=form)
