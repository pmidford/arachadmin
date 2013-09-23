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
           print "Need to update %s, date is %s" % (ont.name,str(date))
           type_name = db.ontology_processing[ont.processing].type_name
           ont_domain = ont.domain
           terms = update_ontology(ont,type_name)
           updateCount = 0
           for term in terms:
               t = None
               new_id = -1
               if isinstance(term,unicode):
                   t = terms[term]
               elif isinstance(term,dict) and 'about' in term:
                   t = term
               if t:
                   new_id = db.term.insert(source_id=t['about'])
                   row = db.term[new_id]
                   updateCount = updateCount + 1;
                   if 'label' in t:
                      db(db.term.id==new_id).update(label=t['label'])
                   db(db.term.id==new_id).update(domain=ont.domain)
           print "loaded %d terms from %s" % (updateCount,ont.name)
    redirect('index')
