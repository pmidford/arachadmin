#!/usr/bin/env python
# -*- coding: utf-8 -*-
from gluon import *

def update_uids(db):
    gen_id_counter = _sweep_generated_ids(db)
    gen_id_counter = _update_publications(db, gen_id_counter)
    gen_id_counter = _update_claims(db, gen_id_counter)
    gen_id_counter = _update_individuals(db, gen_id_counter)
    gen_id_counter = _update_narratives(db, gen_id_counter)
    gen_id_counter = _update_participants(db, gen_id_counter)
    gen_id_counter = _update_taxa(db, gen_id_counter)
    gen_id_counter = _update_terms(db, gen_id_counter)
    print "last_id is {0:d}".format(gen_id_counter)
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
def _extract_count(id_str):
    if id_str.startswith(ARACHBPREFIX):
        return int(id_str[len(ARACHBPREFIX):]);
    else:
        print "Bad Prefix '{0}'".format(id_str)
        return -1

def _update_publications(db, gen_id_counter):
    pubs = db().select(db.publication.ALL)
    for pub in pubs:
        if pub.uids is None:
            if pub.generated_id is not None:
                check_uids = db(db.uids.generated_id == pub.generated_id).select()
                if len(check_uids)>0:
                    print "duplicate found: '{0}'".format(pub.generated_id)
                    gen_id_counter += 1
                    pub.generated_id = gen_id_counter
            new_id = db.uids.insert(source_id=pub.doi, generated_id=pub.generated_id)
            db.commit()
            print "New uids id is {0}".format(new_id)
            pub.update_record(uids=new_id)
        else:
            pub_uids = db(uids.id == pub.uids).select()
            if pub_uids.source_id != pub.doi:
                pub_uids.source_id = pub.doi
                pub_uids.update_record()
            if pub_uids.generated_id != pub.generated_id:
                pub_uids.generated_id = pub.generated_id
                pub_uids.update_record()
    return gen_id_counter


def _update_claims(db, gen_id_counter):
    claims = db().select(db.claim.ALL)
    for claim in claims:
        if claim.uids is None:
            if claim.generated_id is not None:
                check_uids = db(db.uids.generated_id == claim.generated_id).select()
                if len(check_uids)>0:
                    print "duplicate found: '{0}'".format(claim.generated_id)
                    gen_id_counter += 1
                    claim.generated_id = gen_id_counter
            new_id = db.uids.insert(source_id = None, generated_id = claim.generated_id)
            claim.uids = new_id
            claim.update_record()
        else:
            claim_uids = db(uids.id == claim.uids).select()
            if claim_uids.source_id is not None:
                claim_uids.source_id = None
                claim_uids.update_record()
            if claim_uids.generated_id != claim.generated_id:
                claim_uids.generated_id = claim.generated_id
                claim_uids.update_record()
    return gen_id_counter


def _update_individuals(db, gen_id_counter):
    individuals = db().select(db.individual.ALL)
    for individual in individuals:
        if individual.uids is None:
            if individual.generated_id is not None:
                check_uids = db(db.uids.generated_id == individual.generated_id).select()
                if len(check_uids)>0:
                    print "duplicate found: '{0}'".format(individual.generated_id)
                    gen_id_counter += 1
                    individual.generated_id = gen_id_counter
            new_id = db.uids.insert(source_id = individual.source_id,
                                    generated_id = individual.generated_id)
            individual.uids = new_id
            individual.update_record()
        else:
            individual_uids = db(uids.id == individual.uids).select()
            if individual_uids.source_id != individual.source_id:
                individual_uids.source_id = individual.source_id
                individual_uids.update_record()
            if individual_uids.generated_id != individual.generated_id:
                individual_uids.generated_id = individual.generated_id
                individual_uids.update_record()
    return gen_id_counter

def _update_narratives(db, gen_id_counter):
    narratives = db().select(db.narrative.ALL)
    for narrative in narratives:
        if narrative.uids is None:
            if narrative.generated_id is not None:
                check_uids = db(db.uids.generated_id == narrative.generated_id).select()
                if len(check_uids)>0:
                    print "duplicate found: '{0}'".format(narrative.generated_id)
                    gen_id_counter += 1
                    narrative.generated_id = gen_id_counter
            new_id = db.uids.insert(source_id = None, generated_id = narrative.generated_id)
            narrative.uids = new_id
            narrative.update_record()
        else:
            narrative_uids = db(uids.id == narrative.uids).select()
            if narrative_uids.source_id is not None:
                narrative_uids.source_id = None
                narrative_uids.update_record()
            if narrative_uids.generated_id != narrative.generated_id:
                narrative_uids.generated_id = narrative.generated_id
                narrative_uids.update_record()
    return gen_id_counter

def _update_participants(db, gen_id_counter):
    participants = db().select(db.participant.ALL)
    for participant in participants:
        if participant.uids is None:
            if participant.generated_id is not None:
                check_uids = db(db.uids.generated_id == participant.generated_id).select()
                if len(check_uids)>0:
                    print "duplicate found: '{0}'".format(participant.generated_id)
                    gen_id_counter += 1
                    participant.generated_id = gen_id_counter
            new_id = db.uids.insert(source_id = None, generated_id = participant.generated_id)
            participant.uids = new_id
            participant.update_record()
        else:
            participant_uids = db(uids.id == participant.uids).select()
            if participant_uids.source_id is not None:
                participant_uids.source_id = None
                participant_uids.update_record()
            if participant_uids.generated_id != participant.generated_id:
                participant_uids.generated_id = participant.generated_id
                participant_uids.update_record()
    return gen_id_counter

def _update_taxa(db, gen_id_counter):
    taxa = db().select(db.taxon.ALL)
    for taxon in taxa:
        if taxon.uids is None:
            if taxon.generated_id is not None:
                check_uids = db(db.uids.generated_id == taxon.generated_id).select()
                if len(check_uids)>0:
                    print "duplicate found: '{0}'".format(taxon.generated_id)
                    gen_id_counter += 1
                    taxon.generated_id = gen_id_counter
            new_id = db.uids.insert(source_id = taxon.external_id, generated_id = taxon.generated_id)
            taxon.uids = new_id
            taxon.update_record()
        else:
            taxon_uids = db(uids.id == taxon.uids).select()
            if taxon_uids.source_id != taxon.source_id:
                taxon_uids.source_id = taxon.source_id
                taxon_uids.update_record()
            if taxon_uids.generated_id != taxon.generated_id:
                taxon_uids.generated_id = taxon.generated_id
                taxon_uids.update_record()
    return gen_id_counter


def _update_terms(db, gen_id_counter):
    terms = db().select(db.term.ALL)
    for term in terms:
        if term.uids is None:
            if term.generated_id is not None:
                check_uids = db(db.uids.generated_id == term['generated_id']).select()
                if len(check_uids)>0:
                    print "duplicate found: '{0}' ".format(term['generated_id'])
                    gen_id_counter += 1
                    term.generated_id = gen_id_counter
            new_id = db.uids.insert(source_id = term.source_id, generated_id = term.generated_id)
            term.uids = new_id
            term.update_record()
        else:
            term_uids = db(uids.id == term.uids).select()
            if term_uids.source_id != term.source_id:
                term_uids.source_id = term.source_id
                term_uids.update_record()
            if term_uids.generated_id != term.generated_id:
                term_uids.generated_id = term.generated_id
                term_uids.update_record()
    return gen_id_counter
