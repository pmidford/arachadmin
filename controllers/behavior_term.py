# coding: utf8
# try something like
def index():
    redirect(URL('list'))
    
def list():
    return dict(behavior_terms=db().select(db.behavior_term.ALL, orderby=db.behavior_term.id))
    
def show():
    behavior_terms = db.behavior_term(request.args(0,cast=int)) or redirect(URL('list'))
    form = SQLFORM(db.behavior_term)
    return dict(behavior_terms=behavior_terms)
    
def enter():
    if request.args(0):
        behavior_terms = db.behavior_term(request.args(0,cast=int))
        form = SQLFORM(db.behavior_term,behavior_terms)
    else:
        form = SQLFORM(db.behavior_term)
    if form.process().accepted:
        response.flash = 'behavior term table modified'
    elif form.errors:
        response.false = 'errors in submission'
    return dict(form=form)
