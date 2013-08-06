# coding: utf8
# try something like
def index():
    redirect(URL('list'))
    
def list():
    assertions = db().select(db.assertion.ALL, orderby=db.assertion.id)
    return dict(assertions=assertions)
    
def show():
    assertion = db.assertion(request.args(0,cast=int)) or redirect(URL('list'))
    form = SQLFORM(db.assertion)
    return dict(assertion=assertion)
    
def enter():
    if request.args(0):
        assertion = db.assertion(request.args(0,cast=int))
        form = SQLFORM(db.assertion,assertion)
    else:
        form = SQLFORM(db.assertion)
    if form.process().accepted:
        response.flash = 'assertion table modified'
    elif form.errors:
        response.false = 'errors in submission'
    return dict(form=form)
    
def status_tool():
    a = db.assertion
    return
