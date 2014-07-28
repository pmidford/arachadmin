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
    
    form = SQLFORM(db.participant)
    return {'form': form}


def get_builder_args(req):
    if req.args(0):
        participant = req.args(0, cast=int)
    elif req.vars['participant']:
        participant = int(req.vars['participant'])
    else:
        raise Exception("builder had no participant specified")
    if req.args(1):
        element = req.args(1, cast=int)
    elif req.vars['element']:
        element = int(req.vars['element'])
    else:
        element = None
    return (participant,element)


def element():
    """ """
    index = get_element_args(request)
    if index:
        form = SQLFORM(db.participant_element,index)
    else:
        form = SQLFORM(db.participant_element)
    form.vars.participant = 1;
    if form.accepts(request,session):
        element = form.vars.id
        redirect(URL('element2/' + str(element)))
    return {'form': form}


def get_element_args(req):
    """ """
    if req.args(0):
        element = req.args(0, cast=int)
    elif req.vars['element']:
        element = int(req.vars['element'])
    else:
        element = None
    return element


INDIVIDUAL_ELEMENT = 3
SOME_ELEMENT = 1
ONLY_ELEMENT = 2

def element2():
    """ """
    index = get_element_args(request)
    element = db.participant_element[index]
    etype = element['type']
    if etype == INDIVIDUAL_ELEMENT:
        form = SQLFORM(db.pelement2individual, fields=['individual'])
    elif (etype == SOME_ELEMENT) or (etype == ONLY_ELEMENT):
        form = SQLFORM(db.pelement2term, fields=['term'])
    else:
        redirect(URL('element3/' + str(element)))
    form.vars.element = element
    if form.accepts(request,session):
        link = form.vars.id
        redirect(URL('element2/' + str(element)))
    return {'form': form}


def element3():
    """ """
    pass
