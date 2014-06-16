# coding: utf8

def index():
    """default is a list of narratives and their publications"""
    redirect(URL('list'))

def list():
    """
    """
    narratives = db().select(db.narrative.ALL)
    result = [(narrative.id, 
               narrative.label, 
               db.publication(narrative.publication).author_list,
               db.publication(narrative.publication).publication_year) 
              for narrative in narratives] 
    return {"items": result}

        
