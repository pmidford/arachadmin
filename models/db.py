import os
from ConfigParser import SafeConfigParser

defaults = dict(
    host="localhost",
    user="user",
    password="userpass",
    dbname="arachadmin")

conf = SafeConfigParser(defaults)

user = password = dbname = host = ''

if os.path.isfile("applications/%s/private/localconfig" % request.application):
    conf.read("applications/%s/private/localconfig" % request.application)
    host = conf.get("db", "host")
    user = conf.get("db", "user")
    password = conf.get("db", "password")
    dbname = conf.get("db", "dbname")

else:
    conf.read("applications/%s/private/config" % request.application)
    host = conf.get("db", "host")
    user = conf.get("db", "user")
    password = conf.get("db", "password")
    dbname = conf.get("db", "dbname")


db = DAL("mysql://%s:%s@%s/%s" % (user, password, host, dbname), migrate=True)

db.define_table(
    'publication_curation',
    Field('status', 'string', writable=False, length=31),
    format='%(status)s',
    migrate=False)

db.define_table(
    'author',
    Field('last_name', 'string', writable=False, length=63),
    Field('given_names', 'string', writable=False, length=63),
    Field('assigned_id', 'string'),
    Field('generated_id', 'string', writable=False),
    Field('merge_set', 'reference author_merge', ondelete='NO ACTION'),
    format='%(last_name)s',
    migrate=False)

db.define_table(
    'author_merge',
    Field('preferred', 'reference author', ondelete='NO ACTION'),
    format='%(id)s',
    migrate=False)

db.define_table(
    'publication',
    Field('publication_type', 'string', length=31),
    Field('dispensation', 'string', length=31),
    Field('downloaded', 'date'),
    Field('reviewed', 'date'),
    Field('title', 'text', length=255),
    Field('alternate_title', 'text', length=255),
    Field('author_list', 'text'),
    Field('editor_list', 'text'),
    Field('source_publication', 'string'),
    Field('volume', 'integer'),
    Field('issue', 'string'),
    Field('serial_identifier', 'string'),
    Field('page_range', 'string'),
    Field('publication_date', 'string'),
    Field('publication_year', 'string'),
    Field('doi', 'string'),
    Field('generated_id', 'string', writable=False),
    Field(
        'curation_status',
        'reference publication_curation',
        requires=IS_EMPTY_OR(IS_IN_DB(
                db,
                'publication_curation.id',
                '%(status)s'))),
    Field('curation_update', 'datetime'),
    format='%(author_list)s (%(publication_year)s)',
    migrate=False)

db.define_table(
    'authorship',
    Field(
        'publication',
        'reference publication',
        requires=IS_IN_DB(
            db,
            'publication.id',
            '%(author_list)s'),
        ondelete='CASCADE'),
    Field(
        'author',
        'reference author',
        requires=IS_IN_DB(
            db,
            'author.id',
            '%(last_name)s, %(first_name)s'),
        ondelete='CASCADE'),
    Field('position', 'integer'),
    format='%(publication)s',
    migrate=False)

db.define_table(
    'domain',
    Field('name', 'string'),
    format='%(name)s',
    migrate=False)

db.define_table(
    'authority',
    Field('name', 'string'),
    Field('uri', 'string'),
    Field('domain', 'reference domain', ondelete='NO ACTION'),
    format='%(name)s',
    migrate=False)

db.define_table(
    'term',
    Field('source_id', 'string'),
    Field('authority', 'reference authority', ondelete='NO ACTION'),
    Field('domain', 'reference domain', ondelete='NO ACTION'),
    Field('label', 'string'),
    Field('generated_id', 'string', writable=False),
    Field('comment', 'string'),
    format='%(label)s',
    migrate=False)

behavior_domain_id = db(db.domain.name == 'behavior').select().first().id
behavior_domain = db(db.term.domain == behavior_domain_id)
anatomy_domain_id = db(db.domain.name == 'anatomy').select().first().id
anatomy_domain = db(db.term.domain == anatomy_domain_id)  # need to fix this
taxonomy_domain_id = db(db.domain.name == 'taxonomy').select().first().id
taxon_domain = db(db.term.domain == taxonomy_domain_id)
evidence_domain_id = db(db.domain.name == 'evidence').select().first().id
evidence_domain = db(db.term.domain == evidence_domain_id)

db.define_table(
    'synonym',
    Field('text', 'string', length=512),
    Field('term', 'reference term'),
    migrate=False)

db.define_table(
    'individual',
    Field('source_id', 'string', length=512),
    Field('generated_id', 'string', length=512, writable=False),
    migrate=False)

db.define_table(
    'taxon',
    Field('name', 'string', length=512),
    Field('author', 'string', length=512),
    Field('year', 'string', length=512),
    Field('external_id', 'string', length=64),
    Field('authority', 'reference authority', ondelete='NO ACTION'),
    Field(
        'parent',
        'reference taxon',
        requires=IS_EMPTY_OR(IS_IN_DB(db, 'taxon.id', '%(name)s'))),
    Field('generated_id', 'string', length=512, writable=False),
    Field('parent_term', 'reference term'),
    Field('merged', 'boolean', writable=False),
    Field('merge_status', 'string', length=64),
    format='%(name)s',
    migrate=True)

db.taxon.parent_term.requires = IS_EMPTY_OR(
    IS_IN_DB(taxon_domain, 'term.id', '%(label)s'))

db.define_table(
    'taxonomy_authority',
    Field('name', 'string', length=512),
    format='%(name)s',
    migrate=False)

db.define_table(
    'evidence_code',
    Field('long_name', 'string', length=512),
    Field('obo_id', 'string', length=512),
    Field('code', 'string', length=512),
    migrate=False)

def render_participant(r):
    """
    generates pidgin functional owl syntax for a participant
    """
    if r.label:
        return r.label
    if r.quantification == 'some':
        quan = 'some'
    else:
        quan = ''
    if r.anatomy and r.taxon:
        head = "%s of %s" % (db.term(r.anatomy).label, db.term(r.taxon).label)
    elif r.taxon:
        head = str(db.term(r.taxon).label)
    else:
        head = str(db.term(r.substrate).label)
    return "%s %s" % (quan, head)

db.define_table(
    'participant',
    Field('taxon', 'reference term'),
    Field('anatomy', 'reference term'),
    Field(
        'substrate',
        'reference term',
        requires=IS_EMPTY_OR(IS_IN_DB(db, 'term.id', '%(label)s'))),
    Field(
        'quantification',
        'string',
        length=16,
        requires=IS_NULL_OR(IS_IN_SET(["some", "individual"]))),
    Field('label', 'string'),
    Field('publication_taxon', 'string'),
    Field('publication_anatomy', 'string'),
    Field('publication_substrate', 'string'),
    Field('generated_id', 'string', writable=False),
    format=render_participant,
    migrate=False)

db.participant.taxon.requires = IS_EMPTY_OR(
    IS_IN_DB(taxon_domain, 'term.id', '%(label)s'))
db.participant.anatomy.requires = IS_EMPTY_OR(
    IS_IN_DB(anatomy_domain, 'term.id', '%(label)s'))
db.participant.substrate.requires = IS_EMPTY_OR(
    IS_IN_DB(anatomy_domain, 'term.id', '%(label)s'))

db.define_table(
    'claim',
    Field('publication', db.publication),
    Field('publication_behavior', 'string'),
    Field('behavior_term', 'reference term'),
    Field(
        'taxon',
        'reference taxon',
        requires=IS_EMPTY_OR(IS_IN_DB(db, 'taxon.id', '%(name)s'))),
    Field(
        'primary_participant',
        'reference participant',
        requires=IS_EMPTY_OR(
            IS_IN_DB(db, 'participant.id', render_participant))),
    Field('evidence', 'reference evidence_code'),
    Field('generated_id', 'string', writable=False),
    format='Claim: %(generated_id)s',
    migrate=False)

db.claim.behavior_term.requires = IS_EMPTY_OR(
    IS_IN_DB(behavior_domain, 'term.id', '%(label)s'))

db.define_table(
    'claim2term',
    Field('claim', 'reference claim'),
    Field('term', 'reference term'),
    migrate=False)

db.define_table(
    'anatomy2claim',
    Field('anatomy_term', 'reference anatomy_term'),
    Field('claim', 'reference claim'),
    migrate=False)

db.define_table(
    'actor2claim',
    Field('actorID', 'string', length=512),
    Field('claim', 'reference claim'),
    migrate=False)

db.define_table(
    'participant2claim',
    Field('claim', 'reference claim'),
    Field('participant', 'reference participant'),
    Field('participant_index', 'integer'),
    migrate=False)

# defines the source of a supporting ontology
#  name - human friendly name of the ontology
#  source_url - cannonical location for loading the ontology 
#    (e.g., a purl that redirects)
#  processing - specifies a set of rules for processing the ontology file
#  last_update - timestamp on the file in the cannonical location 
#    last time it was checked
#  authority - generally the maintainer of the ontology
#  domain - semantic domain (e.g., taxonomy, behavior, etc.) 
#    covered by the ontology

db.define_table(
    'ontology_source',
    Field('name', 'string', length=512),
    Field('source_url', 'string', length=512),
    Field('processing',
          'reference ontology_processing',
          requires=IS_EMPTY_OR(
            IS_IN_DB(db, 'ontology_processing.id', '%(type_name)s'))),
    Field('last_update', 'datetime', writable=False),
    Field('authority', 'reference authority'),
    Field('domain', 'reference domain', ondelete='NO ACTION'),
    format='Ontology: %(name)',
    migrate=False)

db.define_table(
    'ontology_processing',
    Field('type_name', 'string', length=512),
    format='Ontology processing: %(type_name)',
    migrate=False)
