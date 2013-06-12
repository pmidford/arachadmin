# coding: utf8
# try something like
def index():
    redirect(URL('list'))
    
def list():
    return dict(anatomy_terms=db().select(db.anatomy_term.ALL, orderby=db.anatomy_term.id))
    
def show():
    anatomy_terms = db.anatomy_term(request.args(0,cast=int)) or redirect(URL('list'))
    form = SQLFORM(db.anatomy_term)
    return dict(anatomy_terms=anatomy_terms)
    
def enter():
    if request.args(0):
        anatomy_terms = db.anatomy_term(request.args(0,cast=int))
        form = SQLFORM(db.anatomy_term,anatomy_terms)
    else:
        form = SQLFORM(db.anatomy_term)
    if form.process().accepted:
        response.flash = 'behavior term table modified'
    elif form.errors:
        response.false = 'errors in submission'
    return dict(form=form)
