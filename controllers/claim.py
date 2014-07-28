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
    claim_arg, participant_arg = get_args(request)
    if claim_arg and participant_arg:
        claim = db.claim(claim_arg)
        participant = db.participant(participant_arg)
        link_table = make_link_table(claim)
        main_form = SQLFORM(db.claim, claim)
        participant_form = SQLFORM(db.participant, participant)
        element_list = []
        elements = db(db.participant_element.participant == 
                      participant.id).select()
        if elements:
            element_list = [element.id for element in elements]
    elif claim_arg:
        claim = db.claim(claim_arg)
        link_table = make_link_table(claim)
        main_form = SQLFORM(db.claim, claim)
        participant_form = SQLFORM(db.participant)
        element_list = []
    else:
        main_form = SQLFORM(db.claim)
        participant_form = SQLFORM(db.participant)
        link_table = []
        element_list = []
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
            "element_list": element_list}

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
    """Something to update dthe representation of participants"""
    result = []
    claims = db().select(db.claim.ALL, orderby=db.claim.id)
    for claim in claims:
        rows = db(db.participant2claim.claim == claim.id).select()
        if len(rows) > 0:
            participants = [row.participant for row in rows]
            for participant in participants:
                p_id = participant.id
                elements = db(db.participant_element.participant == 
                              participant.id).select()
                if elements:
                    pass
                else:
                    if participant.taxon:
                        db.participant_element.insert(participant=p_id)
                    if participant.anatomy:
                        db.participant_element.insert(participant=p_id)
                    if participant.substrate:
                        db.participant_element.insert(participant=p_id)
                result.append((p_id,len(elements))) 
    return {'update_report': result }

def row_count(rows):
    count = 0
    for row in rows:
        count += 1

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
