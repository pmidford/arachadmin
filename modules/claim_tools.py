#!/usr/bin/env python
# coding: utf8


def issues_list(claim,db):
    """Generates a list of issues that should be addressed for each 
    claim in the database"""
    # from gluon import *
    p_list = db(db.participant2claim.claim == claim.id).select()
    if len(p_list) == 0:
        return [("No participants", make_claim_url(claim.id))]
    issues = []
    for p in p_list:
        part_id = p.participant
        check = check_participant(db, claim, part_id)
        issues.extend(check)
    return issues


def check_participant(db, claim, part_id):
    """Generates a list of issues for a single participant"""
    # from gluon import *
    p = db(db.participant.id == part_id).select().first()
    link = make_participant_url(claim, p)
    p_issues = []
    if p.quantification == None:
        p_issues.append(("Null participant quantification", link))
    return p_issues


def make_descr(claim):
    return None


def make_claim_url(claim_id):
    """
    generates url that links to the editing page for this claim
    """
    from gluon.html import URL
    return URL('claim', 'enter/' + str(claim_id))


def make_participant_url(claim, participant):
    """
    generates url that links to editing page for this claim and its
    primary participant
    """
    from gluon.html import URL
    return URL('claim',
               'enter/%d/%d' % (claim, participant))


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='check for testing option')
    parser.add_argument("--test", help="activate testing", action="store_true")
    parser.add_argument("--verbose", help="verbose test output", action="store_true")
    args = parser.parse_args()
    if args.test:
        import doctest
        if args.verbose:
            doctest.testmod(verbose=True)
        else:
            doctest.testmod(verbose=False)
