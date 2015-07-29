#!/usr/bin/env python
# -*- coding: utf-8 -*-
from gluon import *

# This is a fixup tool to resolve problems that appeared when moving uids into their
# own table.  The functions here scan each table that has associated uids and checks
# the associated uidset row (if it exists).  The check either creates the uidset or
# vaidates that the source_id or generated_id are present and agree with the parent
# row.  It also checks that ref_id is present and equal to either source_id 
# (preferentially) or the generated id.  It also checks that generated ids are well
# formed, though this will break once these ids get over 1000


def update_uidsets(db):
    """Entry method; db is required as argument because this
    is a module rather than a controller"""
    gen_id_counter = _sweep_generated_ids(db)
    gen_id_counter = _update_publications(db, gen_id_counter)
    gen_id_counter = _update_claims(db, gen_id_counter)
    gen_id_counter = _update_individuals(db, gen_id_counter)
    gen_id_counter = _update_narratives(db, gen_id_counter)
    gen_id_counter = _update_participants(db, gen_id_counter)
    gen_id_counter = _update_taxa(db, gen_id_counter)
    gen_id_counter = _update_terms(db, gen_id_counter)
    print "last_id is {0:d}".format(gen_id_counter)
    _update_all_ref_ids(db)
    return

def _sweep_generated_ids(db):
    last_id = -1
    for pub in db().select(db.publication.ALL):
        if pub.generated_id is not None:
            id = _extract_count(pub.generated_id)
            if id > last_id:
                last_id = id
    for claim in db().select(db.claim.ALL):
        if claim.generated_id is not None:
            id = _extract_count(claim.generated_id)
            if id > last_id:
                last_id = id
    for individual in db().select(db.individual.ALL):
        if individual.generated_id is not None:
            id = _extract_count(individual.generated_id)
            if id > last_id:
                last_id = id
    for narrative in db().select(db.narrative.ALL):
        if narrative.generated_id is not None:
            id = _extract_count(narrative.generated_id)
            if id > last_id:
                last_id = id
    for participant in db().select(db.participant.ALL):
        if participant.generated_id is not None:
            id = _extract_count(participant.generated_id)
            if id > last_id:
                last_id = id
    for taxon in db().select(db.taxon.ALL):
        if taxon.generated_id is not None:
            id = _extract_count(taxon.generated_id)
            if id > last_id:
                last_id = id
    for term in db().select(db.term.ALL):
        if term.generated_id is not None:
            id = _extract_count(term.generated_id)
            if id > last_id:
                last_id = id
    print "last_id was {0:d}".format(last_id)
    return last_id

ARACHBPREFIX = "http://arachb.org/arachb/ARACHB_"
ARACHB0000PREFIX = ARACHBPREFIX+'0000'


def _extract_count(id_str):
    if id_str.startswith(ARACHBPREFIX):
        return int(id_str[len(ARACHBPREFIX):]);
    else:
        print "Bad Prefix '{0}'".format(id_str)
        return -1


def _update_publications(db, gen_id_counter):
    pubs = db().select(db.publication.ALL)
    for pub in pubs:
        if pub.uidset is None:
            if pub.generated_id is not None:
                check_uidset = db(db.uidset.generated_id == pub.generated_id).select()
                if len(check_uidset)>0:
                    print "duplicate found: '{0}'".format(pub.generated_id)
                    gen_id_counter += 1
                    pub.generated_id = ARACHB0000PREFIX + str(gen_id_counter)
            new_id = db.uidset.insert(source_id=pub.doi, generated_id=pub.generated_id)
            db.commit()
            print "New uidset id is {0}".format(new_id)
            pub.update_record(uidset=new_id)
        else:
            pub_uidset = db(db.uidset.id == pub.uidset).select().first()
            if pub_uidset.source_id != pub.doi:
                pub_uidset.source_id = pub.doi
                pub_uidset.update_record()
            if pub_uidset.generated_id != pub.generated_id:
                pub_uidset.generated_id = pub.generated_id
                pub_uidset.update_record()
            elif (pub.generated_id is not None and
                  _extract_count(pub.generated_id) == -1):
                print "trying to fix bad count {0}".format(pub.generated_id)
                gen_id_counter += 1
                pub.generated_id = ARACHB0000PREFIX + str(gen_id_counter)
                pub.update_record()
                pub_uidset.generated_id = pub.generated_id
                pub_uidset.update_record()
    return gen_id_counter


def _update_claims(db, gen_id_counter):
    claims = db().select(db.claim.ALL)
    for claim in claims:
        if claim.uidset is None:
            if claim.generated_id is not None:
                check_uidset = db(db.uidset.generated_id == claim.generated_id).select()
                if len(check_uidset)>0:
                    gen_id_counter += 1
                    claim.generated_id = ARACHB0000PREFIX + str(gen_id_counter)
            new_id = db.uidset.insert(source_id = None, generated_id = claim.generated_id)
            claim.uidset = new_id
            claim.update_record()
        else:
            claim_uidset = db(db.uidset.id == claim.uidset).select().first()
            if claim_uidset.source_id is not None:
                claim_uidset.source_id = None
                claim_uidset.update_record()
            if claim_uidset.generated_id != claim.generated_id:
                claim_uidset.generated_id = claim.generated_id
                claim_uidset.update_record()
            elif (claim.generated_id is not None and
                  _extract_count(claim.generated_id)) == -1:
                gen_id_counter += 1
                claim.generated_id = ARACHB0000PREFIX + str(gen_id_counter)
                claim.update_record()
                claim_uidset.generated_id = claim.generated_id
                claim_uidset.update_record()
    return gen_id_counter


def _update_individuals(db, gen_id_counter):
    individuals = db().select(db.individual.ALL)
    for individual in individuals:
        if individual.uidset is None:
            if individual.generated_id is not None:
                check_uidset = db(db.uidset.generated_id == individual.generated_id).select()
                if len(check_uidset)>0:
                    print "duplicate found: '{0}'".format(individual.generated_id)
                    gen_id_counter += 1
                    individual.generated_id = ARACHB0000PREFIX + str(gen_id_counter)
            new_id = db.uidset.insert(source_id = individual.source_id,
                                    generated_id = individual.generated_id)
            individual.uidset = new_id
            individual.update_record()
        else:
            individual_uidset = db(db.uidset.id == individual.uidset).select().first()
            if individual_uidset.source_id != individual.source_id:
                individual_uidset.source_id = individual.source_id
                individual_uidset.update_record()
            if individual_uidset.generated_id is None:  #participants w/o gen_id
                gen_id_counter += 1
                individual.generated_id = ARACHB0000PREFIX + str(gen_id_counter)
                individual.update_record()
                individual_uidset.generated_id = individual.generated_id
                individual_uidset.ref_id = individual.generated_id
                individual_uidset.update_record()
            if individual_uidset.generated_id != individual.generated_id:
                individual_uidset.generated_id = individual.generated_id
                individual_uidset.update_record()
            elif (individual.generated_id is not None and
                  _extract_count(individual.generated_id) == -1):
                print "trying to fix bad count {0}".format(individual.generated_id)
                gen_id_counter += 1
                individual.generated_id = ARACHB0000PREFIX + str(gen_id_counter)
                individual.update_record()
                individual_uidset.generated_id = individual.generated_id
                individual_uidset.update_record()
    return gen_id_counter


def _update_narratives(db, gen_id_counter):
    narratives = db().select(db.narrative.ALL)
    for narrative in narratives:
        if narrative.uidset is None:
            if narrative.generated_id is not None:
                check_uidset = db(db.uidset.generated_id == narrative.generated_id).select()
                if len(check_uidset)>0:
                    print "duplicate found: '{0}'".format(narrative.generated_id)
                    gen_id_counter += 1
                    narrative.generated_id = ARACHB0000PREFIX + str(gen_id_counter)
            new_id = db.uidset.insert(source_id = None, generated_id = narrative.generated_id)
            narrative.uidset = new_id
            narrative.update_record()
        else:
            narrative_uidset = db(db.uidset.id == narrative.uidset).select().first()
            if narrative_uidset.source_id is not None:
                narrative_uidset.source_id = None
                narrative_uidset.update_record()
            if narrative_uidset.generated_id is None:  #participants w/o gen_id
                gen_id_counter += 1
                narrative.generated_id = ARACHB0000PREFIX + str(gen_id_counter)
                narrative.update_record()
            if narrative_uidset.generated_id != narrative.generated_id:
                narrative_uidset.generated_id = narrative.generated_id
                narrative_uidset.update_record()
            elif (narrative.generated_id is not None and
                  _extract_count(narrative.generated_id) == -1):
                print "trying to fix bad count {0}".format(narrative.generated_id)
                gen_id_counter += 1
                narrative.generated_id = ARACHB0000PREFIX + str(gen_id_counter)
                narrative.update_record()
                narrative_uidset.generated_id = narrative.generated_id
                narrative_uidset.update_record()
    return gen_id_counter


def _update_participants(db, gen_id_counter):
    participants = db().select(db.participant.ALL)
    for participant in participants:
        if participant.uidset is None:
            if participant.generated_id is not None:
                check_uidset = db(db.uidset.generated_id == participant.generated_id).select()
                if len(check_uidset)>0:
                    print "duplicate found: '{0}'".format(participant.generated_id)
                    gen_id_counter += 1
                    participant.generated_id = ARACHB0000PREFIX + str(gen_id_counter)
            new_id = db.uidset.insert(source_id = None, generated_id = participant.generated_id)
            participant.uidset = new_id
            participant.update_record()
        else:
            participant_uidset = db(db.uidset.id == participant.uidset).select().first()
            if participant_uidset.source_id is not None:
                participant_uidset.source_id = None
                participant_uidset.update_record()
            if participant_uidset.generated_id is None:  #participants w/o gen_id
                gen_id_counter += 1
                participant.generated_id = ARACHB0000PREFIX + str(gen_id_counter)
                participant.update_record()
            if participant_uidset.generated_id != participant.generated_id:
                participant_uidset.generated_id = participant.generated_id
                participant_uidset.update_record()
            elif (participant.generated_id is not None and
                  _extract_count(participant.generated_id) == -1):
                print "trying to fix bad count {0}".format(participant.generated_id)
                gen_id_counter += 1
                participant.generated_id = ARACHB0000PREFIX + str(gen_id_counter)
                participant.update_record()
                participant_uidset.generated_id = participant.generated_id
                participant_uidset.update_record()
    return gen_id_counter


def _update_taxa(db, gen_id_counter):
    taxa = db().select(db.taxon.ALL)
    for taxon in taxa:
        if taxon.uidset is None:
            if taxon.generated_id is not None:
                check_uidset = db(db.uidset.generated_id == taxon.generated_id).select()
                if len(check_uidset)>0:
                    print "duplicate found: '{0}'".format(taxon.generated_id)
                    gen_id_counter += 1
                    taxon.generated_id = ARACHB0000PREFIX + str(gen_id_counter)
            new_id = db.uidset.insert(source_id = taxon.external_id, generated_id = taxon.generated_id)
            taxon.uidset = new_id
            taxon.update_record()
        else:
            taxon_uidset = db(db.uidset.id == taxon.uidset).select().first()
            if taxon_uidset.source_id != taxon.external_id:
                taxon_uidset.source_id = taxon.external_id
                taxon_uidset.update_record()
            if taxon_uidset.generated_id != taxon.generated_id:
                taxon_uidset.generated_id = taxon.generated_id
                taxon_uidset.update_record()
            elif (taxon.generated_id is not None and
                  _extract_count(taxon.generated_id) == -1):
                print "trying to fix bad count {0}".format(taxon.generated_id)
                gen_id_counter += 1
                taxon.generated_id = ARACHB0000PREFIX + str(gen_id_counter)
                taxon.update_record()
                taxon_uidset.generated_id = taxon.generated_id
                taxon_uidset.update_record()
    return gen_id_counter


def _update_terms(db, gen_id_counter):
    terms = db().select(db.term.ALL)
    for term in terms:
        if term.uidset is None:
            if term.source_id is not None:
                print "term has source_id" + term.source_id
                check_source_uidset = db(db.uidset.source_id == term['source_id']).select()
                if len(check_source_uidset) > 0:
                    new_id = check_source_uidset.first()
                else:
                    new_id = db.uidset.insert(source_id = term.source_id, generated_id = None)
            elif term.generated_id is not None:
                check_uidset = db(db.uidset.generated_id == term['generated_id']).select()
                if len(check_uidset)>0:
                    print "duplicate found: '{0}' ".format(term['generated_id'])
                    gen_id_counter += 1
                    term.generated_id = ARACHB0000PREFIX + str(gen_id_counter)
                new_id = db.uidset.insert(source_id = term.source_id, generated_id = term.generated_id)
            term.uidset = new_id
            term.update_record()
        else:
            term_uidset = db(db.uidset.id == term.uidset).select().first()
            if term_uidset.source_id != term.source_id:
                term_uidset.source_id = term.source_id
                term_uidset.update_record()
            if term_uidset.generated_id != term.generated_id:
                if term.generated_id is not None:
                    check_source_uidset = db(db.uidset.source_id == term.source_id).select()
                    if len(check_source_uidset) > 0:
                        old_id = check_source_uidset.first()
                        if term.source_id == old_id.source_id:
                            term.uidset = old_id
                            term.update_record
                        else:
                            raise Exception("term and uidset match on generated id but not on source id - something is very wrong")
                else:
                    term_uidset.generated_id = term.generated_id
                    term_uidset.update_record()
            elif (term.generated_id is not None and 
                  _extract_count(term.generated_id) == -1):
                gen_id_counter += 1
                term.generated_id = ARACHB0000PREFIX + str(gen_id_counter)
                term.update_record()
                term_uidset.generated_id = term.generated_id
                term_uidset.update_record()
    return gen_id_counter



def _update_all_ref_ids(db):
    for uidset in db().select(db.uidset.ALL):
        if uidset.ref_id is None:
            if uidset.source_id is not None:
                uidset.ref_id = uidset.source_id
                uidset.update_record()
            elif uidset.generated_id is not None:
                uidset.ref_id = uidset.generated_id
                uidset.update_record()
