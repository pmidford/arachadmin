# coding: utf8
# try something like
def index():
    """
    Entry point to the assertion entry tools;
    """
    assertions = db().select(db.ontology_source.ALL, orderby=db.assertion.id)
    result = [assertion for assertion in assertions]
    return {"assertions": result}
    
def list():
    assertions = db().select(db.assertion.ALL, orderby=db.assertion.id)
    return dict(assertions=assertions)
    
def show():
    assertion = db.assertion(request.args(0,cast=int)) or redirect(URL('list'))
    form = SQLFORM(db.assertion)
    return dict(assertion=assertion)
    
def enter():       
    if request.args(0) and request.args(1):
        assertion = db.assertion(request.args(0,cast=int))
        participant = db.participant(request.args(1,case=int))
        link_table = make_link_table(assertion)
        main_form = SQLFORM(db.assertion,assertion)
        participant_form = SQLFORM(db.participant,participant)
    elif request.vars['assertion'] and request.vars['participant']:
        assertion = db.assertion(int(request.vars['assertion']))
        participant = db.participant(int(request.vars['participant']))
        link_table = make_link_table(assertion)
        main_form = SQLFORM(db.assertion,assertion)
        participant_form = SQLFORM(db.participant,participant)    
    elif request.args(0):
        assertion = db.assertion(request.args(0,cast=int))
        link_table = make_link_table(assertion)
        main_form = SQLFORM(db.assertion,assertion)
        participant_form = SQLFORM(db.participant)
    elif request.vars['assertion']:
        assertion = db.assertion(int(request.vars['assertion']))
        link_table = make_link_table(assertion)
        main_form = SQLFORM(db.assertion,assertion)
        participant_form = SQLFORM(db.participant)
    else:
        main_form = SQLFORM(db.assertion)
        participant_form = SQLFORM(db.participant)
        link_table = []
    if main_form.process().accepted:
        assertion = main_form.vars.id
        response.flash = 'assertion table modified'
    elif main_form.errors:
        response.flash = 'errors in assertion submission'
    if participant_form.process().accepted:
        if assertion:
            participant_id = participant_form.vars.id
            existing_links = db((db.participant2assertion.assertion==assertion.id) & 
                                (db.participant2assertion.participant==participant_id)).select()
            other_links = db(db.participant2assertion.assertion==assertion).select()
            if existing_links:
                response.flash = 'participant table unchanged'
                pass
            elif other_links:
                db.participant2assertion.insert(assertion=assertion,
                                                participant=participant_id,
                                                participant_index=len(other_links)+1)
                link_table = make_link_table(assertion)
                response.flash = 'participant table modified'
            else:
                db.participant2assertion.insert(assertion=assertion,
                                                participant=participant_id,
                                                participant_index=1)
                link_table = make_link_table(assertion)
                response.flash = 'participant table modified'
        else:
            response.flash = 'error: no assertion to link participant to'
    elif participant_form.errors:
        response.flash = 'errors in participant submission'
    return dict(main_form=main_form,participant_form=participant_form,link_table=link_table)
    
def make_link_table(assertion):
    rows = db(db.participant2assertion.assertion==assertion.id).select()
    result = []
    for row in rows:
        item = {}
        item['assertion'] = row.assertion
        item['index'] = row.participant_index
        item['participant'] = render_participant(db.participant(row.participant))
        result.append(item)
    return result
        
    
def test():

    autlast = Field("Last_Name","reference db.author")
    autlast.requires = IS_IN_DB(db,db.author.id,'%(last_name)s',zero=T('Choose an author'))

    #autlast.widget=SQLFORM.widgets.autocomplete(request,
    #                                            db.author.id,
    #                                            id_field=db.author.last_name,
    #                                            orderby=db.author.last_name)
    #autlast.default = request.vars.autlast
    pub_behavior = Field("publication_behavior", "string")
    behavior_term = Field("behavior")
    pub_taxon = Field("publication_taxon","string")
    taxon = Field("taxon")
    pub_anatomy = Field("publication_anatomy","string")
    evidence = Field("evidence")
    gen_id = Field("string")
               
    f = SQLFORM.factory(autlast)  #,pub_behavior,behavior_term,pub_taxon,taxon,pub_anatomy,evidence,gen_id)
    if f.process().accepted:
        t = db.author
        print f.vars.author
        #r = t[int(f.vars.publication)]
    
    return dict(form=f)

    
def status_tool():
    a = db.assertion
    return
