# coding: utf8
# try something like


def index():
    """
    default entry point just redirects to list of authors
    """
    redirect(URL('list'))


def list():
    """
    default display is list, sorted by last name
    """
    authors = db().select(db.author.ALL, orderby=db.author.last_name)
    return {"authors": authors}


def show():
    """
    if id is provided, show one author, otherwise redirect to usual list
    """
    author = db.author(request.args(0, cast=int)) or redirect(URL('list'))
    form = SQLFORM(db.author)
    return {"author": author}


def update_tool():
    """
    Entry point for author tool
    """
    import author_tools
    print "Entering update_tool controller"
    authors = db().select(db.author.ALL, orderby=db.author.last_name)
    author_sets = author_tools.build_groups(authors)
    return {"authors": author_sets}

# implement me
def update_groups():
    """
    This is triggered by the submit button on the grouping page
    and should use the state of any displayed checkboxes to retain
    or tear down proposed groupings
    """
    return {'message': "Not implemented"}


def truncate():
    return {}


def really_truncate():
    db.authorship.truncate()
    db.executesql('DELETE FROM author;')
    # shouldn't need to do this
    db.executesql('ALTER TABLE author AUTO_INCREMENT = 100;')
    # db.author.truncate()  ##fails even after truncating authorship
    return {"message": "Done"}
