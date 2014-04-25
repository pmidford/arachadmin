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
            if (old_date_secs is None) or (source_update_secs > old_date_secs):
                print "Need to update %s, date is %s" % (ont.name,
                                                         str(old_date))
                type_name = db.ontology_processing[ont.processing].type_name
                terms = update_ontology(ont,
                                        type_name,
                                        config,
                                        request.application)
                merge_terms(terms, ont)
                t_now = datetime.now()
                db(db.ontology_source.id == ont.id).update(last_update=t_now)
        ont.update()
    redirect('index')


def merge_terms(terms, ont):
    """
    adds any term in terms not in the term table.  String compare of
    id/uri is used for equality.  Probably not sufficient for merging
    taxonomy.
    """
    update_count = 0
    for term in terms:
        temp = None
        new_id = -1
        if isinstance(term, dict) and 'about' in term:
            temp = term
            term_irl = temp['about']
            old_term = db(db.term.source_id == term_irl).select()
            if len(old_term) == 0:
                new_id = db.term.insert(source_id=temp['about'])
                update_count += 1
                new_term = db(db.term.id == new_id)
                if 'label' in temp:
                    new_term.update(label=temp['label'])
                if 'class_comment' in temp:
                    new_term.update(comment=temp['class_comment'])
                new_term.update(domain=ont.domain)
    print "loaded %d terms from %s" % (update_count, ont.name)
