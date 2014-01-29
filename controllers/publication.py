# coding: utf8
# try something like

def index():
    redirect(URL('list'))

def list():
    publications = db().select(db.publication.ALL, orderby=db.publication.author_list)
    return dict(publications=publications)

def show():
    publication = db.publication(request.args(0,cast=int)) or redirect(URL('list'))
    form = SQLFORM(db.publication)
    return dict(publication=publication)
    
def enter():
    if request.args(0):
        publication = db.publication(request.args(0,cast=int))
        form = SQLFORM(db.publication,publication)
    else:
        form = SQLFORM(db.publication)
    if form.process().accepted:
        response.flash = 'publication table modified'
    elif form.errors:
        response.false = 'errors in submission'
    return dict(form=form)
    
## This needs a filter so rejected (or unreviewed) publications can be hidden and
## ignored by the citation collision logic    
def status_tool():
    '''
    Entry point to the publication status tools;
    lists the current publications by citation and reports status
    the view provides buttons to invoke check_update and update_dois
    '''
    import publication_tools
    publications = db().select(db.publication.ALL, orderby=db.publication.author_list)
    result = []
    for publication in publications:
       issues = publication_tools.issues_list(publication,db)
       pub_item = (publication_tools.make_citation(publication), issues,
                   publication.id)
       result.append(pub_item)
    return {"report": result}

def check_update():
    '''
    This tool will correct whatever problems can be resolved automatically, in particular:
      - generating citations and updating db records (or deleting citations if they have become ambiguous)
    '''
    publications = db().select(db.publication.ALL, orderby=db.publication.author_list)
    for publication in publications:
        update_author(publication)
    return

BADNAMES = ['et al.']

def update_author(pub):
    import publication_tools
    authors = pub.author_list.split(';')
    for author in authors:
        author = author.strip()
        names = author.split(',')
        this_last_name = names[0]
        this_given_names = "".join(names[1:]).strip()
        if this_last_name not in BADNAMES: 
            print "names = %s" % str(names)
            author_rows = db(db.author.last_name == this_last_name).select()
            if len(author_rows) > 0:
                no_match = True
                for author_row in author_rows:
                    if no_match:
                       if author_row['given_names'] == this_given_names:
                           no_match = False
                if no_match:
                    db.author.insert(last_name=this_last_name,given_names=this_given_names)
            else:
                db.author.insert(last_name=this_last_name,given_names=this_given_names)


def update_dois():
    '''
    This tool will attempt to find dois, either by querying crossref directly or by walking the curator through the query process
    '''
    return
