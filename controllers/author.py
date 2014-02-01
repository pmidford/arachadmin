# coding: utf8
# try something like
def index():
    redirect(URL('list'))

def list():
    authors = db().select(db.author.ALL, orderby=db.author.last_name)
    return dict(authors=authors)

def show():
    author = db.author(request.args(0,cast=int)) or redirect(URL('list'))
    form = SQLFORM(db.author)
    return dict(author=author)
    
def update_tool():
    authors = db().select(db.author.ALL, orderby=db.author.last_name)
    return dict(authors=authors)

def truncate():
    return dict()

def really_truncate():
    db.authorship.truncate()
    db.executesql('DELETE FROM author;')
    db.executesql('ALTER TABLE author AUTO_INCREMENT = 100;')  #shouldn't need to do this
    #db.author.truncate()  ##fails even after truncating authorship
    return dict(message="Done")
