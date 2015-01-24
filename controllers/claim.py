# Coding: utf8
"""Controller for claims (statements about observed or generalized
occurances of behavior)"""

PART_OF_URI = 'http://purl.obolibrary.org/obo/BFO_0000050'
PARTICIPATES_IN_URI = 'http://purl.obolibrary.org/obo/BFO_0000056'
ACTIVELY_PARTICIPATES_IN_URI = 'http://purl.obolibrary.org/obo/RO_0002217'


def index():
    """
    Entry point to the claim entry tools;
    """
    claims = db().select(db.ontology_source.ALL, orderby=db.claim.id)
    result = [claim for claim in claims]
    return {"claims": result}


def list():
    """
    generates a page listing claims - ids (should change this) are
    links to the edit page for the claim
    """
    from claim_tools import make_claim_url, make_participant_url
    claims = db().select(db.claim.ALL, orderby=db.claim.id)
    results = []
    for claim in claims:
        primary = get_primary_participant(claim)
        pub = db.publication(claim.publication)
        if primary:
            item = {'id': claim.id,
                    'link': make_participant_url(claim.id, primary),
                    'behavior': claim.publication_behavior,
                    'participant': render_participant(primary),
                    'publication_authors': pub.author_list,
                    'publication_year': pub.publication_year
                    }
        else:
            item = {'id': claim.id,
                    'link': make_claim_url(claim.id),
                    'behavior': claim.publication_behavior,
                    'publication_authors': pub.author_list,
                    'publication_year': pub.publication_year
                    }
        results.append(item)
    return {"items": results}


def show():
    """
    Show a single claim if argument is specified or default back
    to the (default) list
    """
    claim = (db.claim(request.args(0, cast=int)) or
             redirect(URL('list')))
    form = SQLFORM(db.claim)
    return {"claim": claim}


def enter():
    """drives loading of several form components to enable editing of
    claims and participants
    """
    claim = None
    behavior = None
    add_d3_files()
    claim_arg, participant_arg = get_args(request)
    if claim_arg:
        link_table = make_link_table(db.claim(claim_arg))
        var_set = {'claim': claim_arg}
        claim = db.claim(claim_arg)
        (element_list, edge_list) = build_element_graph(claim)
    else:
        element_list = []
        edge_list = []
        link_table = []
        var_set = {}
    if participant_arg:
        assert claim_arg is not None
        var_set = {'participant': participant_arg,
                   'claim': claim_arg,
                   'element': -1*claim_arg}
    claim_form_load = LOAD('claim',
                           'claim_form.load',
                           vars=var_set,
                           target='claim_form',
                           ajax=True,
                           content='loading claim editor')
    participant_load = LOAD('participant',
                            'participant_form.load',
                            target='participant_head',
                            vars=var_set,
                            ajax=True,
                            content='loading participant editor')
    return {'claim_form': claim_form_load,
            'participant_form': participant_load,
            "link_table": link_table,
            "element_list": element_list,
            "edge_list": edge_list}


def get_args(req):
    if req.args(0):
        claim = req.args(0, cast=int)
    elif req.vars['claim']:
        claim = int(req.vars['claim'])
    else:
        claim = None
    if req.args(1):
        participant = req.args(1, cast=int)
    elif req.vars['participant']:
        participant = int(req.vars['participant'])
    else:
        participant = None
    return (claim, participant)


def claim_form():
    claim = request.vars['claim']
    form = SQLFORM(db.claim, claim)
    if form.process().accepted:
        print request.vars.claim
    return {'form': form}


def head_form():
    partic = request.vars['participant']
    if partic is None:
        return LOAD('participant',
                    'head_form.load',
                    target='participant_head',
                    vars={'participant': participant_arg},
                    ajax=True,
                    content='loading head editor')
    else:
        form = SQLFORM(db.participant, partic)
        if form.process().accepted:
            print request.vars
        return {'form': form}


def make_participant_form(part_id=None):
    if part_id:
        partic = db.participant[part_id]
        pubstr = partic.publication_taxon
    else:
        pubstr = ''
    fields = make_initial_participant_fields(pubstr)
    submit_fields = [BR(),
                     INPUT(_type='submit')]
    fields.extend(submit_fields)
    form = FORM(*fields)
    return form


def start_individual_head_form(pub_str, claim):
    fields = make_initial_participant_fields(pub_str)
    submit_fields = [BR(),
                     INPUT(_type='submit')]
    fields.extend(submit_fields)
    form = FORM(*fields)
    return form


def make_initial_participant_fields(pubstr):
    return [FIELDSET('publication string',
                     INPUT(_name='publication_string', _value=pubstr)),
            BR(),
            FIELDSET('term',
                     INPUT(_type='radio',
                           _name='participant_type',
                           _value='term')),
            BR(),
            FIELDSET('individual',
                     INPUT(_type='radio',
                           _name='participant_type',
                           _value='individual'))]


def add_d3_files():
    """adds files related to d3 to the list that is loaded with the entry
    page.  Needed since d3 is used for element display."""
    response.files.append(URL('static/js', 'd3.js'))
    response.files.append(URL('static/css', 'd3test.css'))


def get_primary_participant(claim):
    """returns an arbitrary active participant if any exist, or
       another participant if any exist for this claim"""
    properties = get_properties()
    actively = properties['actively_participates_in']
    rows = db((db.participant2claim.claim == claim.id) &
              (db.participant2claim.property == actively)).select()
    if len(rows) > 0:
        return rows[0].participant
    else:
        participates = properties['participates_in']
        rows = db((db.participant2claim.claim == claim.id) &
                  (db.participant2claim.property == participates)).select()
        if len(rows) > 0:
            return rows[0].participant
        else:
            return None


def make_link_table(claim):
    """generates a set of records that each will correspond to a row of
       a display table with links to edit pages for each participant in
       the claim"""
    from claim_tools import make_claim_url, make_participant_url
    rows = db(db.participant2claim.claim == claim.id).select()
    result = []
    for row in rows:
        part = row.participant
        print "row.id: {}".format(row.id)
        print "row.property: {}".format(row.property)
        item = {'claim': row.claim,
                'property': db.property(row.property).label,
                'participant': render_participant(db.participant(part)),
                'participant_link': make_participant_url(claim.id, part)
                }
        result.append(item)
    print "table = {}".format(str(result))
    return result


def update_tool():
    """Something to update the representation of participants"""
    result = []
    (some_code,
     only_code,
     indiv_code,
     intersection_code,
     union_code) = get_participant_codes()
    properties = get_properties()
    claims = db().select(db.claim.ALL, orderby=db.claim.id)
    for claim in claims:
        rows = db(db.participant2claim.claim == claim.id).select()
        if len(rows) > 0:
            participants = [row.participant for row in rows]
            for p_id in participants:
                participant = p_id
                elements = get_elements(p_id)
                if len(elements) == 0:
                    old_claim_update(elements, participant, p_id)
                if participant.substrate:
                    print "found substrate"
                    if not(check_existing_substrate(claim.id)):
                        # assume for now that substrates are SOME expressions
                        substrate_element(participant.substrate, claim.id)
                    else:
                        print "substrate participant exists, not updated"
                elements = get_elements(p_id)
                result.append((p_id, len(elements)))
    update_participants()
    return {'update_report': result}


def old_claim_update(elements, participant, p_id):
    """This should be dead code at this point"""
    tax_id = None
    ana_id = None
    if (1 > 0):
        raise RuntimeException("This code should be dead - old_claim_update")
    print "Test2: %s %s" % (repr(participant), repr(p_id))
    if participant.taxon:
        if (participant.quantification == 'some'):
            tax_id = insert_participant_element(p_id,
                                                some_code)
            insert_element2term_map(tax_id, participant.taxon)
        elif (participant.quantification == 'individual'):
            ind = lookup_individual(participant.label,
                                    participant.taxon,
                                    claim.narrative)
            if ind is None:
                ind = insert_individual(participant.label,
                                        participant.taxon,
                                        claim.narrative)
                tax_id = insert_participant_element(p_id,
                                                    indiv_code)
                insert_element2indiv_map(tax_id, ind)
            else:
                print "participant %d has no taxon" % p_id
                if participant.anatomy:
                    if (participant.quantification == "some"):
                        ana_id = insert_participant_element(p_id,
                                                            some_code)
                        insert_element2term_map(ana_id,
                                                participant.anatomy)
                        insert_participant_link(ana_id,
                                                tax_id,
                                                properties['part_of'])
                        participant.update_record(head_element=ana_id)
                    elif (participant.quantification == 'individual'):
                        ana_label = get_term_label(participant.anatomy)
                        ind_label = ana_label + " of " + participant.label
                        ind = lookup_individual(ind_label,
                                                participant.anatomy,
                                                claim.narrative)
                        if ind is None:
                            ind = insert_individual(ind_label,
                                                    participant.anatomy,
                                                    claim.narrative)
                        ana_id = insert_participant_element(p_id,
                                                            indiv_code)
                        insert_element2indiv_map(ana_id, ind)
                        insert_participant_link(ana_id,
                                                tax_id,
                                                properties['part_of'])
                        participant.update_record(head_element=ana_id)
                    else:
                        print "participant %d has no anatomy" % p_id
    return

def get_elements(p_id):
    '''returns row set of participant elements for this participant'''
    return db(db.participant_element.participant == p_id).select()


def check_existing_substrate(claim_id):
    p_list = db(db.participant2claim.claim == claim_id).select()
    print "in check existing_substrate"
    print p_list
    return len(p_list) == 2


def update_participants():
    '''this will eventually fix a problem where the structure of individual 
    participants is not 
    captured in element chains when used secondarily in subsequent participants'''
    ptc_table = build_participant_chains()


def build_participant_chains():
    ptc_table = {}
    for ptc in all_participants():
        print("participant: {0}".format(ptc.id))
        chain = []
        head = ptc.head_element
        cur_ele = head
        print("current element: {0}".format(cur_ele))
        plink_rows = db(db.participant_link.parent == cur_ele).select()
        while (plink_rows):
            if len(plink_rows) > 1:
                raise RuntimeError("Bad plink")
            chain = extend_pelement_chain(cur_ele, chain)
            plink = plink_rows[0]
            cur_ele = plink.child
            print("current element: {0}".format(cur_ele))
            plink_rows = db(db.participant_link.parent == cur_ele).select()
        chain = extend_pelement_chain(cur_ele, chain)
        ptc_table[ptc] = chain
        print("chain {0}".format(repr(chain)))
    return ptc_table

def extend_pelement_chain(cur_ele, chain):
    eleTerm = db(db.pelement2term.element == cur_ele).select()
    eleIndiv = db(db.pelement2individual.element == cur_ele).select()
    if eleTerm:
        chain_link = ("Term", eleTerm[0].term)
        chain.append(chain_link)
    elif eleIndiv:
        chain_link = ("Individual", eleIndiv[0].individual)
        chain.append(chain_link)
    else:
        print "bad element"
    return chain


def all_participants():
    return db(db.participant.id >0).select()

def substrate_element(sub_term, claim_id):
    # sub_expr is term id of substrate
    some_code = get_participant_code('some_term')
    property_id = get_properties()['participates_in']
    new_part = db.participant.insert()
    element_id = insert_participant_element(new_part, some_code)
    participant = db.participant(new_part)
    participant.update_record(head_element=element_id)
    insert_element2term_map(element_id, sub_term)
    db.participant2claim.insert(claim=claim_id,
                                participant=new_part,
                                property=property_id)


def get_participant_codes():
    some_code = get_participant_code('some_term')
    only_code = get_participant_code('only_term')
    indiv_code = get_participant_code('individual')
    intersection_code = get_participant_code('intersection')
    union_code = get_participant_code('union')
    return (some_code,
            only_code,
            indiv_code,
            intersection_code,
            union_code)


def get_participant_code(type_str):
    return db(db.participant_type.label == type_str).select().first().id


def get_term_label(term_id):
    return db(db.term.id == term_id).select().first().label


PROPERTY_CACHE = {}


def get_properties():
    if PROPERTY_CACHE:
        return PROPERTY_CACHE
    else:
        PROPERTY_CACHE['part_of'] = get_property(PART_OF_URI)
        PROPERTY_CACHE['participates_in'] = get_property(PARTICIPATES_IN_URI)
        active_property = get_property(ACTIVELY_PARTICIPATES_IN_URI)
        PROPERTY_CACHE['actively_participates_in'] = active_property
    return PROPERTY_CACHE


def insert_participant_element(participant_id, type_id):
    return db.participant_element.insert(participant=participant_id,
                                         type=type_id)


def insert_element2term_map(ele_id, term_id):
    print 'Inserting %d to term %d' % (ele_id, term_id)
    p2t_map = db.pelement2term.insert(element=ele_id, term=term_id)
    db.commit()
    print db.pelement2term[p2t_map]
    print 'Done Inserting %d to term %d to %d' % (ele_id, term_id, p2t_map)


def insert_element2indiv_map(ele_id, indiv_id):
    db.pelement2individual.insert(element=ele_id, individual=indiv_id)
    db.commit()


def insert_participant_link(parent_id, child_id, property_id):
    db.participant_link.insert(parent=parent_id,
                               child=child_id,
                               property=property_id)


def lookup_individual(label, term, narrative):
    """first pass at looking up an individual from its label"""
    # TODO: add narrative to this query
    if label is None:
        print "no label in lookup"
        query = db(db.individual.term == term)
    else:
        query = db((db.individual.label == label) &
                   (db.individual.term == term))
    if query.isempty():
        return None
    else:
        rows = query.select()
        if len(rows) == 1:
            return rows.first()
        else:
            print "Multiple matching individuals"
            return rows


def insert_individual(label, term, narrative):
    """looks up an individual by label and term (type) and
       updates db to associate it to the narrative"""
    ind = db.individual.insert(label=label, term=term)
    if narrative:
        db.individual2narrative.insert(individual=ind, narrative=narrative)
    return ind


def build_element_graph(claim):
    """this generates lists of elements and edges"""
    behavior = db.term(claim.behavior_term)
    behavior_id = behavior.id
    behavior_entry = (reduce_label(behavior.label), -1*claim.id)
    p2c_map = db(db.participant2claim.claim == claim).select()
    participants = [row.participant for row in p2c_map]
    elements = []
    for p_id in participants:
        elist = db(db.participant_element.participant == p_id).select()
        elements.extend(elist)
    element_list = []
    edge_list = []
    element_ids = [element.id for element in elements]
    element_labels = [process_p_element(element.id) for element in elements]
    element_ids.insert(0, behavior_id)
    element_labels.insert(0, behavior_entry)
    element_list.extend(element_labels)
    for p_id in participants:
        p_property = db((db.participant2claim.participant == p_id) &
                        (db.participant2claim.claim ==
                         claim.id)).select().first().property
        edge_list.extend(build_edges(element_ids, p_id, p_property))
    print "elements = {0}".format(str(element_list))
    print "links = {0}".format(str(edge_list))
    return (element_list, edge_list)


def process_p_element(element_id):
    """
    generates a label for the term or individual correponding to an element
    """
    p2t = db(db.pelement2term.element == element_id).select().first()
    if p2t:
        term_id = p2t.term
        term = db(db.term.id == term_id).select().first()
        return (reduce_label(term.label), element_id)
    p2i = db(db.pelement2individual.element == element_id).select().first()
    if p2i:
        i_id = p2i.individual
        individual = db(db.individual.id == i_id).select().first()
        return (reduce_label(individual.label), element_id)
    return "Neither"


def reduce_label(label):
    """returns label with spaces converted to underscores"""
    words = label.split(' ')
    return '_'.join(words)


def build_edges(elements, p_id, p_property):
    """builds the graph of elements (terms/individual) in a
    participant and edges that indicate the linking properties"""
    from collections import deque
    head_element = db.participant[p_id].head_element
    eque = deque()
    eque.append(head_element)
    done = set()
    print "head element is {0}".format(head_element)
    results = [(0,
                elements.index(head_element),
                property_color_lookup(p_property))]
    while len(eque) > 0:
        parent = eque.popleft()
        if parent not in done:
            links = db(db.participant_link.parent == parent).select()
            print "links = %s" % repr(links)
            for link in links:
                child = link.child
                print "link.property {}".format(link.property)
                property_color = property_color_lookup(link.property)
                child_index = elements.index(child)
                parent_index = elements.index(parent)
                results.append((child_index, parent_index, property_color))
                eque.append(child)
            done.add(parent)
    return results


def process_p_link(element_id, id_list):
    """returns list of pairs of child and parent elements at ends of link;
       these are coded by their position in the id_list, which seems to
       be what the d3 code wants to see"""
    links = db(db.participant_link.parent == element_id).select()
    result = []
    for link in links:
        child = link.child
        parent = link.parent
        property_color = property_color_lookup(link.property)
        child_index = id_list.index(child)
        parent_index = id_list.index(parent)
        result.append((child_index, parent_index, property_color))
    return result


PROPERTY_COLORS = {}


def property_color_lookup(property_id):
    if not(PROPERTY_COLORS):
        properties = get_properties()
        print "prop = {0}, properties = {1}".format(property_id,
                                                    repr(properties))
        PROPERTY_COLORS[properties['part_of']] = 'blue'
        PROPERTY_COLORS[properties['participates_in']] = 'orange'
        PROPERTY_COLORS[properties['actively_participates_in']] = 'red'
    if property_id in PROPERTY_COLORS:
        return PROPERTY_COLORS[property_id]
    else:
        return 'black'


def status_tool():
    """Scans the set of claims in the database and generates
    a list of issues to fix."""
    import claim_tools
    claims = db().select(db.claim.ALL)
    result = []
    for claim in claims:
        issues = claim_tools.issues_list(claim, db)
        if issues:
            for issue in issues:
                claim_item = (claim.publication_behavior,
                              issue[0],
                              issue[1])
                result.append(claim_item)
    return {"report": result}
