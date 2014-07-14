# coding: utf8

def index():
    """default is a list of participants and their claims"""
    redirect(URL('list'))

def list():
    """
    """
    participants = db().select(db.participant.ALL)
    result = [(participant.id, )
              for participant in participants] 
    return {"items": result}

def enter():
    """
    provides a form for creating/editing a narrative record
    """
    if request.args(0):
        participant = db.participant(request.args(0, cast=int))
        form = SQLFORM(db.participant, participant)
    else:
        form = SQLFORM(db.participant)
    if form.process().accepted:
        response.flash = 'participant table modified'
    elif form.errors:
        response.flash = 'errors in submission'
    return {'form': form}


def builder():
    """ """
    
    form = FORM(db.participant)
    return {'form': form}

def get_builder_args(req):
    if req.args(0):
        participant = req.args(0, cast=int)
    elif req.vars['participant']:
        participant = int(req.vars['participant'])
    else:
        raise new Exception("builder had no participant specified")
    if req.args(1):
        element = req.args(1, cast=int)
    elif req.vars['element']:
        element = int(req.vars['element'])
    else:
        element = None
    return (participant,element)
