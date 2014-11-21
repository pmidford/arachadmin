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


def participant_form():
    print request.vars
    if request.vars.participant is None:
        return new_participant_form()
    else:
        form = SQLFORM(db.participant, request.vars.participant)
        if form.process().accepted:
            print request.vars.head
        return {'form': form}

PARTICIPATES_IN_URI = 'http://purl.obolibrary.org/obo/BFO_0000056'
ACTIVELY_PARTICIPATES_IN_URI = 'http://purl.obolibrary.org/obo/RO_0002217'


def new_participant_form():
    fields = make_initial_participant_fields()
    fields.append(BR())
    fields.append(INPUT(_type='submit'))
    form=FORM(*fields)
    if form.process().accepted:
        claim_id = request.vars.claim
        part_type = form.vars.participant_type
        pub_text = form.vars.publication_string
        property_name = form.vars.property
        if property_name == 'active participant':
            property = get_predicate(ACTIVELY_PARTICIPATES_IN_URI)
        else:
            property = get_predicate(PARTICIPATES_IN_URI)
        var_set = {'publication_text': pub_text,
                   'property': property.id,
                   'claim': claim_id}
        if part_type == 'individual':
            pass
        else:  # assume term
            term_participant_form = LOAD('participant',
                                         'term_participant_form.load',
                                         target='participant_head',
                                         vars=var_set,
                                         ajax=True,
                                         content='loading participant editor')
            return {'form': term_participant_form}
    return {'form': form}


def make_initial_participant_fields():
    return [DIV(FIELDSET('publication string',
                         INPUT(_name='publication_string')),
                BR()),
            DIV('Choose term or individual participant',
                BR(),
                make_labeled_button('term', 'participant_type'),
                BR(),
                make_labeled_button('individual', 'participant_type'),
                BR()),
            DIV('Choose participant level',
                BR(),
                make_labeled_button('active participant', 'property'),
                BR(),
                make_labeled_button('participant', 'property'))]

                     

def make_labeled_button(val, group):
    return FIELDSET(val,
                    INPUT(_type='radio',
                          _name=group,
                          _value=val))


def element_initial():
    form=FORM(INPUT(_type='text',_name='element'),
              BR(),
              INPUT(_type='submit'))
    if form.process().accepted:
        print request.vars.element
    return {'form': form}



def term_participant_form():
    form = FORM('Choose a domain',
                make_labeled_button('taxonomy', 'domain'),
                BR(),
                make_labeled_button('anatomy', 'domain'),
                BR(),
                INPUT(_type='submit'))
    if form.process().accepted:
        claim_id = request.vars.claim
        property_id = request.vars.property
        pub_text = request.vars.publication_text        
        domain = form.vars.domain
        assert pub_text is not None, 'pub text is None'
        assert claim_id is not None, 'claim_id is None'
        assert property_id is not None, 'property is None'
        assert domain is not None, 'domain is None'
        var_set = {'publication_text': pub_text,
                   'domain': domain,
                   'property': property_id,
                   'claim': claim_id}
        term_from_domain_form = LOAD('participant',
                                     'term_from_domain.load',
                                     target='participant_head',
                                     vars=var_set,
                                     ajax=True,
                                     content='loading participant editor')
        return {'form': term_from_domain_form}
    return {'form': form}


def term_from_domain():
    if request.vars.domain == 'taxonomy':
        field_domain = taxon_domain
    elif request.vars.domain == 'anatomy':
        field_domain = anatomy_domain
    else:
        field_domain = term
    form = SQLFORM.factory(Field('term',
                                 'reference term',
                                 requires=IS_EMPTY_OR(IS_IN_DB(field_domain,
                                                               'term.id',
                                                               '%(label)s'))))
    if form.process().accepted:
        print request.vars
        pub_text = request.vars.publication_text
        claim_id = request.vars.claim
        property_id = request.vars.property
        term_id = form.vars.term
        assert pub_text is not None, 'pub text is None'
        assert claim_id is not None, 'claim_id is None'
        assert property_id is not None, 'property is None'
        assert term_id is not None, 'term_id is None'
        new_part = db.participant.insert(publication_text=pub_text)
        some_code = get_participant_code('some_term')
        element_id = insert_participant_element(new_part, some_code)
        head_id = insert_participant_head(element_id, claim_id, property_id)
        insert_element2term_map(element_id, term_id)
        db.participant2claim.insert(claim=claim_id,
                                    participant=new_part,
                                    participant_index=2)  # should fix
        var_set = {'claim': claim_id,
                   'participant': new_part}
        return LOAD('participant',
                    'participant_form.load',
                    vars=var_set,
                    ajax=True,
                    content='reloading participant editor')
    return form


def enter():
    """ Improved element focussed entry """
    form = FORM(FIELDSET('term',
                         INPUT(_type='radio',
                               _name='participant_type',
                               _value='term')),
                BR(),
                FIELDSET('individual',
                         INPUT(_type='radio',
                               _name='participant_type',
                               _value='individual')),
                BR())
    if form.process().accepted:  # validators?
        type_label = db.participant_type(form.vars.type).label
        property_label = db.property(form.vars.property).label
        print "type_label is {}".format(type_label)
        print "property is {}".format(property_label)
        if type_label == 'individual':
            print "want to load finish_individual"
            return LOAD("participant",
                        'finish_individual.load',
                        target='add_element',
                        ajax=True,
                        content='loading individual editor....')
        elif type_label in TERM_TYPES:
            print "want to load finish_term"
            choose_vars = {'element_type': form.vars.type,
                           'property': property,
                           'parent': parent}
            return LOAD("participant",
                        'choose_domain.load',
                        vars=choose_vars,
                        target='add_element',
                        ajax=True,
                        content='loading term editor....')
        else:
            print "Fell through"
    return {'form': form}

def insert_participant_head(head_ele, claim, prop):
    db.participant_head.insert(head=head_ele,
                               claim=claim,
                               property=prop)



# def enter():
#     """
#     provides a form for creating/editing a narrative record
#     """
#    if request.args(0):
#        participant = db.participant(request.args(0, cast=int))
#        form = SQLFORM(db.participant, participant)
#    else:
#        form = SQLFORM(db.participant)
#    if form.process().accepted:
#        response.flash = 'participant table modified'
#    elif form.errors:
#        response.flash = 'errors in submission'
#    return {'form': form}


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
        if ele > 0:
            eler = db.participant_element[ele]
            print "eler is %s" % repr(eler)
            lnr = db(db.participant_link.child == ele).select()
            print "lnr is %s" % repr(lnr)
            lnt = make_element_link_table(lnr)
            print "lnt is %s" % repr(lnt)
            etx = lookup_pelement_term_map(ele)
            if etx:
                ee = etx['term']
                etl = db.term[ee].label
            else:
                etx = lookup_pelement_individual_map(ele)
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
        else:  # should be behavior term; treat as claim
            print "hit claim"
            # LOAD(f="add_participant_click", target='add_element')
            return None
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
        child_part = row.child
        child_m2 = lookup_pelement_term_map(child_part)
        if child_m2:
            child_entity = db.term[child_m2.term]
        else:
            child_m2 = lookup_pelement_individual_map(child_part)
            if child_m2:
                child_entity = db.individual(child_m2.individual)
            else:
                child_entity = None
        parent_part = row.parent
        parent_m2 = lookup_pelement_term_map(parent_part)
        if parent_m2:
            parent_entity = db.term[parent_m2.term]
        else:
            parent_m2 = lookup_pelement_individual_map(parent_part)
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


def lookup_pelement_term_map(element):
    return db(db.pelement2term.element == element).select().first()


def lookup_pelement_individual_map(element):
    return db(db.pelement2individual.element == element).select().first()


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
    form = SQLFORM.factory(Field('type',
                                 'reference participant_type',
                                 requires=IS_EMPTY_OR(IS_IN_DB(db,
                                                               'participant_type.id',
                                                               '%(label)s'))),
                           Field('property',
                                 'reference property',
                                 requires=IS_EMPTY_OR(IS_IN_DB(db,
                                                               'property.id',
                                                               '%(label)s'))))
    if form.process().accepted:  # validators?
        type_label = db.participant_type(form.vars.type).label
        property_label = db.property(form.vars.property).label
        print "type_label is {}".format(type_label)
        print "property is {}".format(property_label)
        if type_label == 'individual':
            print "want to load finish_individual"
            return LOAD("participant",
                        'finish_individual.load',
                        target='add_element',
                        ajax=True,
                        content='loading individual editor....')
        elif type_label in TERM_TYPES:
            print "want to load finish_term"
            choose_vars = {'element_type': form.vars.type,
                           'property': property,
                           'parent': parent}
            return LOAD("participant",
                        'choose_domain.load',
                        vars=choose_vars,
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
        finish_vars = {'domain': domain,
                       'element_type': element_type,
                       'parent': parent}
        return LOAD("participant",
                    'finish_term.load',
                    vars=finish_vars,
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
                                 requires=IS_EMPTY_OR(IS_IN_DB(field_domain,
                                                               'term.id',
                                                               '%(label)s'))))
    if form.process().accepted:
        term = form.vars.term
        parent = request.vars.parent
        participant_type_id = request.vars.element_type
        print "selected term {0}".format(str(term))
        print "passed element_type is {0}".format(request.vars.element_type)
        print "passed parent is {0}".format(parent)
        print "participant_code {0}".format(participant_type_id)
        participant_id = lookup_participant(parent)
        print "participant {0}".format(participant_id)
        new_element = insert_participant_element(participant_id,
                                                 participant_type_id)
        print "new element {0}".format(new_element)
        new_map = insert_element2term_map(new_element, term)
        print "new map {0}".format(new_map)
        redirect(request.env.http_web2py_component_location, client_side=True)
    return {'form': form}


def get_participant_code(type_str):
    return db(db.participant_type.label == type_str).select().first().id


def lookup_participant(parent):
    parent_element = db.participant_element(parent)
    return parent_element.participant


def insert_participant_element(participant_id, type_id):
    return db.participant_element.insert(participant=participant_id,
                                         type=type_id)


def lookup_claim(participant_id):
    return db.participant(participant_id).claim


def insert_element2term_map(ele_id, term_id):
    return db.pelement2term.insert(element=ele_id, term=term_id)


def finish_child():
    parent = get_element_args(request)
    eler = db.participant_element(ele)
    insert_participant_link(parent, ele, get_partof_property())
    # need to set up the parent links
    print "eler is %s" % repr(eler)
    lnr = db(db.participant_link.child == ele).select()
    print "lnr is %s" % repr(lnr)
    lnt = make_element_link_table(lnr)
    print "lnt is %s" % repr(lnt)
    (entity, entity_label) = get_entity(ele)
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

# new stuff getting called from the head edit pane in claim.py

def start_individual_head():
    return None

def start_term_head():
    return None




def get_term_map_for_ele(ele):
    """get the pelement2term mapping for this element"""
    # TODO: should be unique
    return db(db.pelement2term.element == ele).select().first()


def get_individual_map_for_ele(ele):
    """get the pelement2individual mapping for this element"""
    # TODO: should be unique
    return db(db.pelement2individual.element == ele).select().first()


PART_OF_URI = 'http://purl.obolibrary.org/obo/BFO_0000050'

def get_partof_property():
    return db(db.property.source_id == PART_OF_URI).select().first()

def insert_participant_link(parent_id, child_id, property_id):
    db.participant_link.insert(child=child_id,
                               parent=parent_id,
                               property=property_id)

