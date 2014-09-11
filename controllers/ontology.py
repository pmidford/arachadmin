# coding: utf8


def index():
    """
    Entry point to the ontology load/update tools;
    """
    ontologies = db().select(db.ontology_source.ALL)
    result = [ontology for ontology in ontologies]
    return {"ontologies": result}

_CONF_OBJ_DICT = {}


def get_conf(request, domain):
    """
    Lifted from phylografter's externalproc.py (so presumibly originally
    from Mark Holder), this manages configuration for ontology parsing.
    This allows definition of domain specific parsing and filtering rules
    (once fully implemented)
    """
    global _CONF_OBJ_DICT
    app_name = request.application
    config = _CONF_OBJ_DICT.get(app_name)
    if config is None:
        from ConfigParser import SafeConfigParser
        config = SafeConfigParser({})
        config.read("applications/%s/private/config" % request.application)
        _CONF_OBJ_DICT[app_name] = config
    return config

UPDATE_FORMAT = "%a, %d %b %Y %H:%M:%S GMT"


def check_modified():
    """
    for each source in the ontology source table, pulls the uri,
    tries to determine a last modified date, then reloads the ontology
    into the terms table if the date in source is older than the date
    retrived from the uri.
    """
    from ontology_tools import check_date, update_ontology
    from datetime import datetime
    import time
    config = get_conf(request, '')  # domain not currently used
    ontologies = db().select(db.ontology_source.ALL)
    for ont in ontologies:
        source_update = check_date(ont.source_url)
        if source_update != '':
            source_update_struct = time.strptime(source_update.rstrip(),
                                                 UPDATE_FORMAT)
        else:
            source_update_struct = None
        if source_update_struct:
            source_update_secs = time.mktime(source_update_struct)
        else:
            source_update_secs = None
        old_date = ont.last_update
        if old_date:
            old_date_struct = old_date.utctimetuple()
        else:
            old_date_struct = None
        if old_date_struct:
            old_date_secs = time.mktime(old_date_struct)
        else:
            old_date_secs = None
        if source_update_secs or True:
            if (old_date_secs is None) or (source_update_secs > old_date_secs) or True:
                print "Need to update %s, date is %s" % (ont.name,
                                                         str(old_date))
                type_name = db.ontology_processing[ont.processing].type_name
                (classes, object_properties) = update_ontology(ont,
                                                               type_name,
                                                               config,
                                                               request.application)
                merge_terms(classes, ont)
                merge_properties(object_properties, ont)
                t_now = datetime.now()
                db(db.ontology_source.id == ont.id).update(last_update=t_now)
        ont.update()
    redirect('index')


def merge_terms(parsed_terms, ont):
    """
    adds any term in terms not in the term table.  String compare of
    id/uri is used for equality.  Probably not sufficient for merging
    taxonomy.
    """
    update_count = 0
    for termvals in parsed_terms:
        new_id = -1
        if isinstance(termvals, dict) and 'about' in termvals:
            term_irl = termvals['about']
            old_term = db(db.term.source_id == term_irl).select().first()
            if old_term is None:
                new_id = db.term.insert(source_id=termvals['about'])
                update_count += 1
                new_term = db(db.term.id == new_id).select().first()
                fill_new_item(new_term, termvals)
                new_term.domain = ont.domain
                new_term.update_record()
    print "loaded %d terms from %s" % (update_count, ont.name)


def fill_new_item(item, values):
    if 'label' in values:
        item.label = values['label']
    if 'comment' in values:
        item.comment = values['comment']
    
    

def merge_properties(properties, ont):
    """
    adds any property in properties not in the property table.  String compare of
    id/uri is used for equality.  
    """
    update_count = 0
    for propvals in properties:
        new_id = -1
        if isinstance(propvals, dict) and 'about' in propvals:
            prop_irl = propvals['about']
            old_prop = db(db.property.source_id == prop_irl).select().first()
            if old_prop is None:
                new_id = db.property.insert(source_id=propvals['about'])
                update_count += 1
                new_prop = db(db.property.id == new_id).select().first()
                fill_new_item(new_prop, propvals)
                new_prop.domain = ont.domain
                new_prop.update_record()
    print "loaded %d object properties from %s" % (update_count, ont.name)
