# coding: utf8

def index():
    """default is a list of narratives and their publications"""
    redirect(URL('list'))

def list():
    """
    """
    narratives = db().select(db.narrative.ALL)
    result = [(narrative.id, 
               narrative.label, 
               db.publication(narrative.publication).author_list,
               db.publication(narrative.publication).publication_year) 
              for narrative in narratives] 
    return {"items": result}

def enter():
    """
    provides a form for creating/editing a narrative record
    """
    if request.args(0):
        narrative = db.narrative(request.args(0, cast=int))
        form = SQLFORM(db.narrative, narrative)
    else:
        form = SQLFORM(db.narrative)
    if form.process().accepted:
        response.flash = 'narrative table modified'
    elif form.errors:
        response.flash = 'errors in submission'
    return {'form': form}
