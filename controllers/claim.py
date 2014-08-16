# coding: utf8


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
    response.files.append(URL('static/js','d3.js'))
    response.files.append(URL('static/css', 'd3test.css'))
    element_list = []
    edge_list = []
    claim_arg, participant_arg = get_args(request)
    if claim_arg and participant_arg:
        claim = db.claim(claim_arg)
        participant = db.participant(participant_arg)
        link_table = make_link_table(claim)
        main_form = SQLFORM(db.claim, claim)
        participant_form = SQLFORM(db.participant, participant)
        elements = db(db.participant_element.participant == 
                      participant.id).select()
        if elements:
            element_ids = [element.id for element in elements]  
            element_labels = [process_p_element(element.id) for element in elements]
            print "%s; %s" % (str(element_ids),str(element_labels))
            element_list = element_labels
            edge_list = [process_p_link(element.id,element_ids) for element in elements]
            print "links = %s" % str(edge_list)
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
    return (claim,participant)

def get_primary_participant(claim):
    rows = db((db.participant2claim.claim == claim.id) &
              (db.participant2claim.participant_index == 1)).select()
    if len(rows) == 1:
        return rows[0].participant


def make_link_table(claim):
    """
    """
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
    claims = db().select(db.claim.ALL, orderby=db.claim.id)
    for claim in claims:
        rows = db(db.participant2claim.claim == claim.id).select()
        if len(rows) > 0:
            participants = [row.participant for row in rows]
            for participant in participants:
                p_id = participant.id
                elements = db(db.participant_element.participant == 
                              participant.id).select()
                if len(elements)>0:
                    pass
                else:
                    tax_ele_id = None
                    ana_ele_id = None
                    sub_ele_id = None
                    if participant.taxon:
                        print "q = %s" % participant.quantification
                        if (participant.quantification == 'some'):
                            tax_ele_id = insert_participant_element(p_id,some_code)
                            db.pelement2term.insert(element=tax_ele_id,
                                                    term=participant.taxon)
                        elif (participant.quantification == 'individual'):
                            tax_ele_id = insert_participant_element(p_id,individual_code)
                            db.pelement2term.insert(element=tax_ele_id,
                                                    term=participant.taxon)
                    if participant.anatomy:
                        print "q = %s" % participant.quantification
                        if (participant.quantification == "some"):
                            ana_ele_id = insert_participant_element(p_id,some_code)
                            db.pelement2term.insert(element=ana_ele_id,
                                                    term=participant.anatomy)
                    if participant.substrate:
                        print "q = %s" % participant.quantification
                        if (participant.quantification == "some"):
                            sub_ele_id = insert_participant_element(p_id,some_code)
                            db.pelement2term.insert(element=sub_ele_id,
                                                    term=participant.anatomy)
                result.append((p_id,len(elements))) 
    return {'update_report': result }

def get_participant_codes():
    some_code = get_participant_code('some_term')
    only_code = get_participant_code('only_term')
    individual_code = get_participant_code('individual')
    intersection_code = get_participant_code('intersection')
    union_code = get_participant_code('union')
    return (some_code,only_code,individual_code,intersection_code,union_code)

def get_participant_code(type_str):
    return db(db.participant_type.label == type_str).select().first().id


def insert_participant_element(participant_id,type_id):
    return db.participant_element.insert(participant=participant_id,type=type_id)


def row_count(rows):
    count = 0
    for row in rows:
        count += 1


def process_p_element(element_id):
    terms = db(db.pelement2term.element == element_id).select()
    if len(terms) > 0:
        return "term"
    individuals = db(db.pelement2individual.element == element_id).select()
    if len(individuals) > 0:
        return "individual"
    return "Neither"


def process_p_link(participant_id,id_list):
    links = db(db.participant_link.child == 
               participant_id).select()
    return (0,1)
    if len(links)>0:
        return [(0,1)]  #fake return
        # return [(links[0].child,links[0].parent)]
    return None

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


def view_participant():
    """Don't really need to treat participant records as first class
    entities, but want a place to display and edit chains"""


def edit_participant():
    """a stub for now"""
