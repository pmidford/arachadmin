#!/usr/bin/env python
# coding: utf8
from gluon import *

def issues_list(claim,db):
    p_list = db(db.participant2claim.claim == claim.id).select()
    if len(p_list) == 0:
        return [("No participants", make_claim_url(claim))]
    issues = []
    for p in p_list:
        part_id = p.participant
        check = check_participant(db, claim, part_id)
        issues.extend(check)
    return issues

def check_participant(db, claim, part_id):
   p = db(db.participant.id == part_id).select()
   assert len(p) == 1
   participant = p[0]
   link = make_participant_url(claim, participant)
   p_issues = []
   if participant.quantification == None:
       p_issues.append(("Null participant quantification", link))
   return p_issues


def make_descr(claim):
    return None

def make_claim_url(claim):
    """
    generates url that links to the editing page for this claim
    """
    return URL('claim', 'enter/' + str(claim.id))

def make_participant_url(claim, participant):
    """
    generates url that links to editing page for this claim and its
    primary participant
    """
    return URL('claim',
               'enter/%d/%d' % (claim, participant))


