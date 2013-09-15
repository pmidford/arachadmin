# coding: utf8
from ontology_tools import check_date
def index():
    '''
    Entry point to the ontology load/update tools;
    '''
    import ontology_tools
    ontologies = db().select(db.ontology_source.ALL)
    result = [ontology for ontology in ontologies]
    return {"ontologies": result}
    
def check_modified():
    from ontology_tools import check_date,update_ontology
    ontologies = db().select(db.ontology_source.ALL)
    for ont in ontologies:
        date = check_date(ont.source_url)
        old_date = ont.last_update
        if (old_date is None) or (date > old_date):
           print "Need to update, date is %s" % str(date)
           update_ontology(db,ont)
    redirect('index')
