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
    return dict(items=results)


def make_participant_url(claim, participant):
    """
    generates url that links to editing page for this claim and its
    primary participant
    """
    return URL('claim',
               'enter/%d/%d' % (claim, participant))


def make_claim_url(claim):
    """
    generates url that links to the editing page for this claim
    """
    return URL('claim', 'enter/' + str(claim.id))


def show():
    claim = (db.claim(request.args(0, cast=int)) or
             redirect(URL('list')))
    form = SQLFORM(db.claim)
    return dict(claim=claim)


def enter():
    if request.args(0) and request.args(1):
        claim = db.claim(request.args(0, cast=int))
        participant = db.participant(request.args(1, cast=int))
        link_table = make_link_table(claim)
        main_form = SQLFORM(db.claim, claim)
        participant_form = SQLFORM(db.participant, participant)
    elif request.vars['claim'] and request.vars['participant']:
        claim = db.claim(int(request.vars['claim']))
        participant = db.participant(int(request.vars['participant']))
        link_table = make_link_table(claim)
        main_form = SQLFORM(db.claim, claim)
        participant_form = SQLFORM(db.participant, participant)
    elif request.args(0):
        claim = db.claim(request.args(0, cast=int))
        link_table = make_link_table(claim)
        main_form = SQLFORM(db.claim, claim)
        participant_form = SQLFORM(db.participant)
    elif request.vars['claim']:
        claim = db.claim(int(request.vars['claim']))
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
    return dict(main_form=main_form,
                participant_form=participant_form,
                link_table=link_table)


def get_primary_participant(claim):
    rows = db((db.participant2claim.claim == claim.id) &
              (db.participant2claim.participant_index == 1)).select()
    if len(rows) == 1:
        return rows[0].participant


def make_link_table(claim):
    rows = db(db.participant2claim.claim == claim.id).select()
    result = []
    for row in rows:
        item = {'claim': row.claim,
                'index': row.participant_index,
                'participant': render_participant(db.participant(
                    row.participant)),
                'participant_link': make_participant_url(claim.id,
                                                         row.participant)
                }
        result.append(item)
    return result


def status_tool():
    a = db.claim
    return
