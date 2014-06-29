# coding: utf8

def index():
    """default is a list of individuals, their narratives and claims"""
    redirect(URL('list'))

def list():
    """scaffold/auditing tool"""
    individuals = db().select(db.individual.ALL)
    result = [(individual.id, )
              for individual in individuals]
    return {"items": result}

def enter():
    """provides an entry form.  This form should be scaffolding -
    individuals should be generated in the process of defining
    participants"""
    if request.args(0):
        individual = db.individual(request.args(0, cast = int))
        form = SQLFORM(db.individual, individual)
    else:
        form - SQL(db.individual)
    if form.process().accepted:
        response.flash = 'individual table modified'
    elif form.errors:
        response.flash = 'errors in submission'
    return {'form': form}
