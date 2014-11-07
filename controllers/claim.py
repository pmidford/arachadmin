# coding: utf8
"""Controller for claims (statements about observed or generalized 
occurances of behavior)"""

def index():
    """
    Entry point to the claim entry tools;
    """
    claims = db().select(db.ontology_source.ALL, orderby=db.claim.id)
    result = [claim for claim in claims]
    return {"claims": result}


def list():
    """
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
                    'link': make_claim_url(claim),
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
    """
    """
    element_list = []
    edge_list = []
    add_d3_files()
    claim_arg, participant_arg = get_args(request)
    if claim_arg and participant_arg:
        claim = db.claim(claim_arg)
        participant = db.participant(participant_arg)
        link_table = make_link_table(claim)
        main_form = SQLFORM(db.claim, claim)
        participant_form = SQLFORM(db.participant, participant)
        elements = db(db.participant_element.participant ==
                      participant.id).select()
        behavior = db(db.term.id == claim.behavior_term).select().first()
        if elements:
            (element_list, edge_list) = process_elements_and_links(behavior,
                                                                   elements)
    elif claim_arg:
        claim = db.claim(claim_arg)
        link_table = make_link_table(claim)
        main_form = SQLFORM(db.claim, claim)
        participant_form = SQLFORM(db.participant)
    else:
        main_form = SQLFORM(db.claim)
        participant_form = SQLFORM(db.participant)
        link_table = []
    if main_form.process().accepted:
        claim = main_form.vars.id
        redirect(URL('claim', 'enter/' + str(claim)))
        response.flash = 'claim table modified'
    elif main_form.errors:
        response.flash = 'errors in claim submission'
    if participant_form.process().accepted:
        if claim:
            participant_id = participant_form.vars.id
            existing_links = db((db.participant2claim.claim ==
                                 claim.id) &
                                (db.participant2claim.participant ==
                                 participant_id)).select()
            other_links = db(db.participant2claim.claim ==
                             claim).select()
            if existing_links:
                response.flash = 'participant updated'
            else:
                if other_links:
                    part_index = len(other_links)+1
                    response.flash = 'new participant added to table'
                else:
                    part_index = 1
                    response.flash = 'participant table modified'
                db.participant2claim.insert(claim=claim,
                                            participant=participant_id,
                                            participant_index=part_index)
                link_table = make_link_table(claim)
        else:
            response.flash = 'error: no claim to link participant to'
    elif participant_form.errors:
        response.flash = 'errors in participant submission'
    return {"main_form": main_form,
            "participant_form": participant_form,
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


def add_d3_files():
    """adds files related to d3 to the list that is loaded with the entry
    page.  Needed since d3 is used for element display."""
    response.files.append(URL('static/js', 'd3.js'))
    response.files.append(URL('static/css', 'd3test.css'))


def get_primary_participant(claim):
    """returns the participant row marked as the primary participant
       for the claim""" 
    rows = db((db.participant2claim.claim == claim.id) &
              (db.participant2claim.participant_index == 1)).select()
    assert len(rows) == 1
    return rows[0].participant


def make_link_table(claim):
    """generates a set of records that each will correspond to a row of
       a display table with links to edit pages for each participant in
       the claim"""
    from claim_tools import make_claim_url, make_participant_url
    rows = db(db.participant2claim.claim == claim.id).select()
    result = []
    for row in rows:
        part = row.participant
        item = {'claim': row.claim,
                'index': row.participant_index,
                'participant': render_participant(db.participant(part)),
                'participant_link': make_participant_url(claim.id, part)
                }
        result.append(item)
    return result


def update_tool():
    """Something to update the representation of participants"""
    result = []
    (some_code,
     only_code,
     individual_code,
     intersection_code,
     union_code) = get_participant_codes()
    (part_of, has_participant) = get_predicates()
    claims = db().select(db.claim.ALL, orderby=db.claim.id)
    for claim in claims:
        rows = db(db.participant2claim.claim == claim.id).select()
        if len(rows) > 0:
            participants = [row.participant for row in rows]
            for participant in participants:
                p_id = participant.id
                elements = db(db.participant_element.participant == 
                              participant.id).select()
                if len(elements) == 0:
                    tax_id = None
                    ana_id = None
                    sub_id = None
                    if participant.taxon:
                        if (participant.quantification == 'some'):
                            tax_id = insert_participant_element(p_id,some_code)
                            head_id = insert_participant_head(tax_id, claim.id)
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
                                                                individual_code)
                            insert_element2indiv_map(tax_id,ind)
                        else:
                            print "participant %d has no taxon" % p_id
                    if participant.anatomy:
                        if (participant.quantification == "some"):
                            ana_id = insert_participant_element(p_id, some_code)
                            insert_element2term_map(ana_id, participant.anatomy)
                            insert_participant_link(tax_id, ana_id, part_of.id)
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
                            ana_id = insert_participant_element(p_id,individual_code)
                            insert_element2indiv_map(ana_id, ind)
                            insert_participant_link(tax_id, ana_id, part_of.id)
                        else:
                            "participant %d has no anatomy" % p_id
                    if participant.substrate:  # assume for now that substrates are always some expressions
                        substrate_element(participant.substrate, p_id, some_code)
                    elements = db(db.participant_element.participant == participant.id).select()
                else:
                    print "participant has existing elements, not updated"
                result.append((p_id,len(elements))) 
    return {'update_report': result }


def substrate_element(sub_term,p_id,some_code):
    # sub_expr is term id of substrate
    print "substrate assumes some quantified"
    sub_id = insert_participant_element(p_id, some_code)
    insert_element2term_map(sub_id, sub_term)
    

def get_participant_codes():
    some_code = get_participant_code('some_term')
    only_code = get_participant_code('only_term')
    individual_code = get_participant_code('individual')
    intersection_code = get_participant_code('intersection')
    union_code = get_participant_code('union')
    return (some_code,only_code,individual_code,intersection_code,union_code)


def get_participant_code(type_str):
    return db(db.participant_type.label == type_str).select().first().id


def get_term_label(term_id):
    return db(db.term.id == term_id).select().first().label


def get_predicates():
    part_of_pred = get_predicate('http://purl.obolibrary.org/obo/BFO_0000050')
    participates_in_pred = get_predicate('http://purl.obolibrary.org/obo/BFO_0000056')
    return (part_of_pred, participates_in_pred)


def get_predicate(uri):
    return db(db.property.source_id == uri).select().first()


def insert_participant_element(participant_id, type_id):
    return db.participant_element.insert(participant=participant_id, type=type_id)


def insert_element2term_map(ele_id,term_id):
    db.pelement2term.insert(element=ele_id, term=term_id)


def insert_element2indiv_map(ele_id,indiv_id):
    db.pelement2individual.insert(element=ele_id, individual=indiv_id)


def insert_participant_link(parent_id, child_id, property_id):
    db.participant_link.insert(child=child_id,
                               parent=parent_id,
                               property=property_id)

def insert_participant_head(head_ele, claim):
    prop = get_predicate('http://purl.obolibrary.org/obo/BFO_0000056')
    db.participant_head.insert(head=head_ele,
                               claim=claim,
                               property=prop)



def lookup_individual(label, term, narrative):
    """first pass at looking up an individual from its label"""
    # to do, add narrative to this query
    if label is None:
        print "no label in lookup"
        q = db(db.individual.term == term)
    else:
        q = db((db.individual.label == label) & (db.individual.term == term))
    if q.isempty():
        return None
    else:
        rows = q.select();
        if len(rows) == 1:
            return rows.first()
        else:
            print "Multiple matching individuals"
            return rows


def insert_individual(label, term, narrative):
    """looks up an individual by label and term (type) and
       updates db to associate it to the narrative"""
    ind = db.individual.insert(label=label, term=term);
    if narrative:
        db.individual2narrative.insert(individual=ind,narrative=narrative)
    return ind


def process_elements_and_links(behavior, elements):
    """this generates lists of elements and edges"""
    behavior_id = behavior.id
    behavior_entry = (reduce_label(behavior.label),-1)
    element_ids = [element.id for element in elements]  
    element_labels = [process_p_element(element.id) for element in elements]
    element_ids.insert(0, behavior_id)
    element_labels.insert(0, behavior_entry)
    print "{}; {}".format(str(element_ids),str(element_labels))
    element_list = element_labels
    edge_list = []
    for element in elements:
        edges = process_p_link(element.id, element_ids)
        edge_list.extend(edges)
    print "links = {0}".format(str(edge_list))
    return (element_list, edge_list)


def process_p_element(element_id):
    """
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


def process_p_link(participant_id,id_list):
    """returns list of pairs of child and parent elements at ends of link; 
       these are coded by their position in the id_list, which seems to
       be what the d3 code wants to see"""
    links = db(db.participant_link.child == 
               participant_id).select()
    result = []
    for link in links:
        child = link.child
        parent = link.parent
        property_color = property_color_lookup(link.property)
        child_index = id_list.index(child)
        parent_index = id_list.index(parent)
        result.append((child_index, parent_index, property_color))
    return result


def property_color_lookup(property):
    source_id = db.property(property).source_id
    if source_id == "http://purl.obolibrary.org/obo/BFO_0000050":
        return "blue"
    else:
        return "black"


def status_tool():
    """
    Scans the set of claims in the database and generates a list of issues to fix.
    """
    import claim_tools
    claims = db().select(db.claim.ALL)
    result = []
    for claim in claims:
        issues = claim_tools.issues_list(claim, db)
        if issues:
            for issue in issues:
                claim_descr = claim.publication_behavior # not very pythonic way of doing this
                claim_item = (claim_descr, issue[0], issue[1])
                result.append(claim_item)
    print result
    return {"report": result}





