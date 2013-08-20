# coding: utf8
def index():
    '''
    Entry point to the ontology load/update tools;
    '''
    import ontology_tools
    ontologies = db().select(db.ontology_source.ALL)
    result = [ontology.name for ontology in ontologies]
    return {"ontologies": result}
