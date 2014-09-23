#!/usr/bin/env python
# coding: utf8
"""A collection of utilities for checking completeness of
a publication citation"""

def check_citation(author_list, year):
    """
    Checks that it is possible to generate a citation (at least
    one author and a year)  Author_list is a string, so
    comparison with 1 is appropriate
    >>> check_citation("Darwin, Charles", 1859)
    True
    >>> check_citation("Darwin, Charles", None)
    False
    >>> check_citation("", None)
    False
    >>> check_citation("", 2014)
    False
    """
    return len(author_list) > 1 and year is not None


def make_citation(author_list, year):
    """
    Generates a label resembling a text citation
    >>> make_citation("Darwin, Charles", 1859)
    'Darwin, Charles (1859)'
    >>> make_citation("Midford, Peter; Arendt, Julie", 2015)
    'Midford, Peter and Arendt, Julie (2015)'
    >>> make_citation("Maddison, Wayne; Midford, Peter; Otto, Sally", 2007)
    'Maddison, Wayne et al. (2007)'
    """
    authors = author_list.split(';')
    if len(authors) == 1:   # single author
        author = authors[0].strip()
        return "{0} ({1})".format(author, year)
    elif len(authors) == 2:
        author1 = authors[0].strip()
        author2 = authors[1].strip()
        return "{0} and {1} ({2})".format(author1, author2, year)
    else:
        author = authors[0].strip()
        return "{0} et al. ({1})".format(author, year)

UPDATE_FAILURE_MSG = "Curation status {0} could not be auto-updated"


def issues_list(pub, db):
    """
    Looks for problems with a publication and returns a list of strings
    identifying these problems
    """
    result = []
    if not check_citation(pub.author_list, pub.publication_year):
        result.append("No Citation")
    ct = db.publication_curation
    if not pub.curation_status:
        stat_row = db(ct.status == pub.dispensation).select().first()
        if stat_row:
            status_id = stat_row.id
            db(db.publication.id == pub.id).update(curation_status=status_id)
        elif pub.dispensation == 'Downloaded':
            status_id = db(ct.status == 'Have PDF').select().first().id
            db(db.publication.id == pub.id).update(curation_status=status_id)
        else:
            result.append(UPDATE_FAILURE_MSG.format(pub.dispensation))
    return result


def split_name(author):
    """Attempts to split an author name into first and last
    """
    a = author.strip()
    names = a.split(',')  # maybe only the first
    last = names[0]
    given = "".join(names[1:]).strip()
    return (last, given)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='check for testing option')
    parser.add_argument("--test", help="activate testing", action="store_true")
    parser.add_argument("--verbose",
                        help="verbose test output",
                        action="store_true")
    args = parser.parse_args()
    if args.test:
        import doctest
        if args.verbose:
            doctest.testmod(verbose=True)
        else:
            doctest.testmod(verbose=False)
