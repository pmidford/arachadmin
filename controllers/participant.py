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


def get_element_args(req):
    """ """
    if req.args(0):
        element = req.args(0, cast=int)
    elif req.vars['element']:
        element = int(req.vars['element'])
    else:
        element = None
    return element


def pelement():
    ele = get_element_args(request)
    if ele:
        eler = db.participant_element[ele]
        print "eler is %s" % repr(eler)
        lnr = db(db.participant_link.child == ele).select()
        print "lnr is %s" % repr(lnr)
        lnt = make_element_link_table(lnr)
        print "lnt is %s" % repr(lnt)
        etx = db(db.pelement2term.element == ele).select().first()
        if etx:
            ee = etx['term']
            etl = db.term[ee].label
        else:
            etx = db(db.pelement2individual.element == ele).select().first()
            if etx:
                ee = etx['individual']
                etl = db.individual[ee].label
            else:
                ee = None
                etl = None
        part_row = render_participant(db.participant[eler.participant])
        print "etr is %s " % repr(ee)
        eform = SQLFORM(db.participant_element,
                        record=ele,
                        fields=['type'],
                        showid=False)
        add_buttons = _build_buttons(ele)
    else:  # maybe make this never happend
        eform = SQLFORM(db.participant_element)

    return dict(ele=ele,
                epart=part_row,
                etr=etl,
                eform=eform,
                lnt=lnt,
                add_buttons=add_buttons)


def _build_buttons(element):
    return {"child_button":
            A(T("Add Child"),
              callback=URL('add_child/' + str(element)),
              target="active_element",
              _class='btn',
              _style='margin-top: 1em;'),
            "sibling_button":
            A(T("Add Sibling"),
              callback=URL('add_sibling/' + str(element)),
              target="active_element",
              _class='btn',
              _style='margin-top: 1em;')}


def make_element_link_table(link_rows):
    result = []
    for row in link_rows:
        print "hit first row"
        child_part = row.child
        child_m2 = db(db.pelement2term.element == child_part).select().first()
        if child_m2:
            child_entity = db.term[child_m2.term]
        else:
            child_m2 = db(db.pelement2individual.element == child_part).select().first()
            if child_m2:
                child_entity = db.individual[child_m2.individual]
            else:
                child_entity = None
        print "got child"
        parent_part = row.parent
        parent_m2 = db(db.pelement2term.element == parent_part).select().first()
        if parent_m2:
            parent_entity = db.term[parent_m2.term]
        else:
            parent_m2 = db(db.pelement2individual.element == parent_part).select().first()
            if parent_m2:
                parent_entity = db.individual[parent_m2.individual]
            else:
                parent_entity = None
        print "got parent"
        property_prop = db.property[row.property]
        item = {'child': child_entity.label,
                'parent': parent_entity.label,
                'property': property_prop.label,
                'row_id': row.id}
        result.append(item)
    print result
    return result


def elementlink():
    """builds form for setting link property of new link"""
    link_id = request.vars['link_id']
    form = SQLFORM(db.participant_link,
                   record=link_id,
                   fields=['property'],
                   showid=False)
    return {'form': form}

TERM_TYPES = ['some_term', 'intersection', 'union', 'only_term']

def add_child():
    parent = get_element_args(request)
    print "parent = {0}".format(parent)
    form = SQLFORM(db.participant_element,
                   fields=['type'])
    if form.process().accepted:  # validators?
        type_label = db.participant_type[form.vars.type].label
        ele = form.vars.id
        print "created {0}".format(ele)
        print "type_label is {}".format(type_label)
        if type_label == 'individual':
            print "want to load finish_individual"
            return LOAD("participant",
                        'finish_individual.load',
                        target='add_element',
                        ajax=True,
                        content='loading individual editor....')
        elif type_label in TERM_TYPES:
            print "want to load finish_term"
            vars = {'element_type': type_label,
                    'parent': parent}
            return LOAD("participant",
                        'choose_domain.load',
                        vars=vars,
                        target='add_element',
                        ajax=True,
                        content='loading term editor....')
        else:
            print "Fell through"
    return {'form': form}


def add_sibling():
    ele = db.participant_element.insert()
    sibling = get_element_args(request)
    print "sibling = {0}".format(parent)
    eform = SQLFORM(db.participant_element,
                    record=ele,
                    fields=['type'])
    return None


def finish_individual():
    form = SQLFORM(db.pelement2individual)
    return {'form': form}


def choose_domain():
    form = FORM('Choose a domain',
                FIELDSET('taxonomy',
                         INPUT(_type='radio', 
                               _name='domain', 
                               _value='taxonomy')),
                BR(),
                FIELDSET('anatomy',
                         INPUT(_type='radio', 
                               _name='domain', 
                               _value='anatomy')),
                BR(),
                INPUT(_type='submit'))
    if form.process().accepted:  # validators?
        element_type = request.vars.element_type
        domain = form.vars.domain
        parent = request.vars.parent
        vars = {'domain': domain,
                'element_type': element_type,
                'parent': parent}
        return LOAD("participant",
                    'finish_term.load',
                    vars = vars,
                    target='add_element',
                    ajax=True,
                    content='loading term editor....')
    return {'form': form}


def finish_term():
    print "want to finish term"
    if request.vars.domain == 'taxonomy':
        field_domain = taxon_domain
    elif request.vars.domain == 'anatomy':
        field_domain = anatomy_domain
    else:
        field_domain = term
    form = SQLFORM.factory(Field('term', 
                                 'reference term',
                                 requires=IS_EMPTY_OR(IS_IN_DB(field_domain,'term.id','%(label)s'))))
    if form.process().accepted:
        term = form.vars.term
        parent = request.vars.parent
        element_type = request.vars.element_type
        participant = request.vars.participant
        print "selected term {0}".format(str(term))
        print "passed element_type is {0}".format(request.vars.element_type)
        print "passed parent is {0}".format(parent)
        # element_type_id = lookup_element_type(request.vars.element_type)
        # participant_id = lookup_participant(parent)
        #pe = insert_pelement()
        #pe2t = insert_pelement2term()
    return {'form': form}


def finish_child():
    parent = get_element_args(request)
    eler = db.participant_element[ele]
    insert_participant_link(parent, ele, get_partof_property())
    # need to set up the parent links
    print "eler is %s" % repr(eler)
    lnr = db(db.participant_link.child == ele).select()
    print "lnr is %s" % repr(lnr)
    lnt = make_element_link_table(lnr)
    print "lnt is %s" % repr(lnt)
    (entity,entity_label) = get_entity(ele)
    # part_row = render_participant(db.participant[eler.participant])
    print "entity is %s " % repr(entity)
    eform = SQLFORM(db.participant_element,
                    record=ele,
                    fields=['type'],
                    showid=False)
    add_buttons = _build_buttons(ele)
    return dict(ele=ele,
                epart="test_row",  # part_row,
                etr=entity_label,
                eform=eform,
                lnt=lnt,
                add_buttons=add_buttons)


def get_entity(ele):
    """finds the entity (term or individual) for this element
       returns the entity id and label"""
    element_entity_map = get_term_map_for_ele(ele)
    if element_entity_map:  # entity is a term
        entity = element_entity_map['term']
        entity_label = db.term[entity].label
        return (entity, entity_label)
    else:
        element_entity_map = get_individual_map_for_ele(ele)
        if element_entity_map:
            entity = element_entity_map['individual']
            entity_label = db.individual[entity].label
            return (entity, entity_label)
        else:
            return (None, None)
            entity = None
            entity_label = None


def get_term_map_for_ele(ele):
    """get the pelement2term mapping for this element"""  
    # TODO: should be unique
    return db(db.pelement2term.element == ele).select().first()


def get_individual_map_for_ele(ele):
    """get the pelement2individual mapping for this element"""
    # TODO: should be unique
    return db(db.pelement2individual.element == ele).select().first()


def old_add_sibling():
    sib = get_element_args(request)
    print "sib = {0}".format(sib)
    ele = db.participant_element.insert()
    eler = db.participant_element[ele]
    # need to set up the parent links
    print "eler is %s" % repr(eler)
    lnr = db(db.participant_link.child == ele).select()
    print "lnr is %s" % repr(lnr)
    lnt = make_element_link_table(lnr)
    print "lnt is %s" % repr(lnt)
    etx = db(db.pelement2term.element == ele).select().first()
    if etx:
        ee = etx['term']
        etl = db.term[ee].label
    else:
        etx = db(db.pelement2individual.element == ele).select().first()
        if etx:
            ee = etx['individual']
            etl = db.individual[ee].label
        else:
            ee = None
            etl = None
        part_row = None #  render_participant(db.participant[eler.participant])
        print "etr is %s " % repr(ee)
        eform = SQLFORM(db.participant_element,
                        record=ele,
                        fields=['type'],
                        showid=False)
        add_buttons = _build_buttons(ele)
    return dict(ele=ele,
                epart=part_row,
                etr=etl,
                eform=eform,
                lnt=lnt,
                add_buttons=add_buttons)


PART_OF_URI = 'http://purl.obolibrary.org/obo/BFO_0000050'


def insert_participant_link(parent_id, child_id, property_id):
    property_id = db(db.property.source_id == PART_OF_URI).select().first()
    db.participant_link.insert(child=child_id,
                               parent=parent_id,
                               property=property_id)


def get_add_args(req):
    """ """
    if req.args(0):
        element = req.args(0, cast=int)
    elif req.vars['element']:
        element = int(req.vars['element'])
    else:
        element = None
    if req.args(1):
        parent = req.args(1, cast=int)
    elif req.vars['parent']:
        parent = int(req.vars['parent'])
    else:
        parent = None
    return element
