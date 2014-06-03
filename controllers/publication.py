# coding: utf8
# try something like


def index():
    """
    Default entry is a list of publications
    """
    redirect(URL('list'))


def list():
    """
    grab all the publications ordered by first author last name
    """
    publications = db().select(db.publication.ALL,
                               orderby=db.publication.author_list)
    return {"publications": publications}


def show():
    """
    Show a single publication
    """
    publication = (db.publication(request.args(0, cast=int)) or
                   redirect(URL('list')))
    form = SQLFORM(db.publication)
    return {"publication": publication}


def enter():
    """
    provides a form for entering a publication
    """
    if request.args(0):
        publication = db.publication(request.args(0, cast=int))
        form = SQLFORM(db.publication, publication)
    else:
        form = SQLFORM(db.publication)
    if form.process().accepted:
        response.flash = 'publication table modified'
    elif form.errors:
        response.false = 'errors in submission'
    return {"form": form}


# This needs a filter so rejected (or unreviewed) publications can be hidden
# and ignored by the citation collision logic
def status_tool():
    """
    Entry point to the publication status tools;
    lists the current publications by citation and reports status
    the view provides buttons to invoke check_update and update_dois
    """
    import publication_tools
    publications = db().select(db.publication.ALL,
                               orderby=db.publication.author_list)
    result = []
    for publication in publications:
        issues = publication_tools.issues_list(publication, db)
        if issues:
            pub_cit = publication_tools.make_citation(publication)
            for issue in issues:
                pub_item = (pub_cit, issues, publication.id)
                result.append(pub_item)
    return {"report": result}


def check_update():
    """
    This tool will correct whatever problems can be resolved automatically,
    in particular:
      - generating citations and updating db records
          (or deleting citations if they have become ambiguous)
    """
    publications = db().select(db.publication.ALL,
                               orderby=db.publication.author_list)
    for publication in publications:
        update_author(publication)
    redirect(URL('publication', 'status_tool'))

BADNAMES = ['et al.']


def update_author(pub):
    """
    update the author list for a signle publication
    """
    import publication_tools
    authors = pub.author_list.split(';')
    for author in authors:
        (this_last, this_given) = publication_tools.split_name(author)
#        author = author.strip()
#        names = author.split(',')
#        this_last_name = names[0]
#        this_given_names = "".join(names[1:]).strip()
        if this_last not in BADNAMES:
            author_rows = db(db.author.last_name == this_last).select()
            if author_rows:
                no_match = True
                for author_row in author_rows:
                    if no_match:
                        if author_row['given_names'] == this_given:
                            no_match = False
                if no_match:
                    new_id = db.author.insert(last_name=this_last,
                                              given_names=this_given)
            else:
                new_id = db.author.insert(last_name=this_last,
                                          given_names=this_given)


def update_dois():
    """
    This tool will attempt to find dois, either by querying crossref
    directly or by walking the curator through the query process
    """
    return
