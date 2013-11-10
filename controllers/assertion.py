# coding: utf8
# try something like
def index():
    """
    Entry point to the ontology update tools;
    """
    assertions = db().select(db.ontology_source.ALL, orderby=db.assertion.id)
    result = [assertion for assertion in assertions]
    return {"ontologies": result}
    
def list():
    assertions = db().select(db.assertion.ALL, orderby=db.assertion.id)
    return dict(assertions=assertions)
    
def show():
    assertion = db.assertion(request.args(0,cast=int)) or redirect(URL('list'))
    form = SQLFORM(db.assertion)
    return dict(assertion=assertion)
    
def enter():
    if request.args(0):
        assertion = db.assertion(request.args(0,cast=int))
        link_table = db(db.participant2assertion.assertion==assertion.id).select(db.participant2assertion.ALL)
        main_form = SQLFORM(db.assertion,assertion)
        participant_form = SQLFORM(db.participant)
    else:
        main_form = SQLFORM(db.assertion)
        participant_form = SQLFORM(db.participant)
        link_table = None
    if main_form.process().accepted:
        response.flash = 'assertion table modified'
    elif main_form.errors:
        response.flash = 'errors in assertion submission'
    if participant_form.process().accepted:
        response.flash = 'participant table modified'
    elif participant_form.errors:
        response.flash = 'errors in participant submission'
    return dict(main_form=main_form,participant_form=participant_form,link_table=link_table)
    
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
