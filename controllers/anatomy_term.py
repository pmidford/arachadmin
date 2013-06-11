# coding: utf8
# try something like
def index():
    redirect(URL('list'))
    
def list():
    usages = db().select(db.term_usage.ALL, orderby=db.term_usage.id)
    return dict(usages=usages)
    
def show():
    usage = db.term_usage(request.args(0,cast=int)) or redirect(URL('list'))
    form = SQLFORM(db.term_usage)
    return dict(usage=usage)
    
def enter():
    if request.args(0):
        usage = db.term_usage(request.args(0,cast=int))
        form = SQLFORM(db.term_usage,usage)
    else:
        form = SQLFORM(db.term_usage)
    if form.process().accepted:
        response.flash = 'usage table modified'
    elif form.errors:
        response.false = 'errors in submission'
    return dict(form=form)
