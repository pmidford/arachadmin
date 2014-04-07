# coding: utf8

def index():
    """
    Entry point to the taxon entry tools;
    """
    redirect(URL('list'))

def list():
    """
    List of non-NCBI taxa and their references"
    """
    taxa = db().select(db.taxon.ALL, orderby=db.taxon.id)
    results = []
    for taxon in taxa:
        rparent = db.term(taxon.parent_term)
        if rparent:
            rparent_id = rparent.source_id
        else:
            rparent_id = None
        item = {'id': taxon.id,
                'name': taxon.name,
                'external_id': taxon.external_id,
                'authority': taxon.authority,
                'author': taxon.author,
                'year': taxon.year,
                'parent': taxon.parent,
                'rooted_parent': rparent_id,
                'merged': taxon.merged,
                'merge_status': taxon.merge_status
                }
        results.append(item)
    return dict(items=results)

def show():
    taxa = db.taxon(request.args(0,cast=int)) or redirect(URL('list'))
    form = SQLFORM(db.taxon)
    return dict(taxa=taxa)

def enter():
    if request.args(0):
        taxon = db.taxon(request.args(0,cast=int))
        form = SQLFORM(db.taxon,taxon)
    else:
        form = SQLFORM(db.taxon)
    if form.process().accepted:
        response.flash = 'taxon table modified'
    elif form.errors:
        response.false = 'errors in submission'
    return dict(form=form)

def merge():
    updateCount = 0;
    domain_q = (db.domain.name=='taxonomy')
    tax_domain_row = db(domain_q).select()
    tax_domain = tax_domain_row[0]['id']
    print tax_domain
    taxa = db().select(db.taxon.ALL)
    for taxon in taxa:
        q = (db.term.label == taxon.name)
        rows = db(q).select()
        if (len(rows)>0):
            print "found term for %s" % taxon.name
            db.taxon[taxon.id]=dict(merged=True)
        elif taxon.parent_term != None:
            new_id = db.term.insert(source_id=taxon['external_id'])
            row = db.term[new_id]
            updateCount = updateCount + 1;
            db.term[new_id]= dict(label=taxon['name'],domain=tax_domain,authority=taxon['authority'])
        else:
            print "didn't find term for %s" % taxon.name
            db.taxon[taxon.id] = dict(merged=False,merge_status='Parent unknown')
    redirect(URL('list'))
