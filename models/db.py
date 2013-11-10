import datetime, socket, os, sys
from ConfigParser import SafeConfigParser

defaults = dict(host="localhost", user="user", password="userpass", dbname="arachadmin")

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


db = DAL("mysql://%s:%s@%s/%s" % (user, password, host, dbname), migrate=True ) 

db.define_table('publication_curation',
                Field('status','string',writable=False,length=31),
                format='%(status)s')
                
db.define_table('author',
                Field('last_name','string',writable=False,length=63),
                Field('first_name','string',writable=False,length=63),
                format='%(last_name)s')
                
db.define_table('publication',
                Field('publication_type','string',length=31),
                Field('dispensation','string',length=31),
                Field('downloaded','date'),
                Field('reviewed','date'),
                Field('title','text',length=255),
                Field('alternate_title','text',length=255),
                Field('author_list','text'),
                Field('editor_list','text'),
                Field('source_publication','string'),
                Field('volume','integer'),
                Field('issue','string'),
                Field('serial_identifier','string'),
                Field('page_range','string'),
                Field('publication_date','string'),
                Field('publication_year','string'),
                Field('doi','string'),
                Field('generated_id','string',writable=False),
                Field('curation_status','reference publication_curation',requires=IS_EMPTY_OR(IS_IN_DB(db,'publication_curation.id','%(status)s'))),
                Field('curation_update','datetime'),
                format = '%(author_list)s (%(publication_year)s)')
                                
db.define_table('authorship',
                Field('publication','reference publication',requires=IS_IN_DB(db,'publication.id','%(author_list)s')),
                Field('author','reference author',requires=IS_IN_DB(db,'author.id','%(last_name)s, %(first_name)s')),
                Field('position','integer'),
                format = '%(publication)s')
                                
db.define_table('domain',
                Field('name','string'),
                format = '%(name)s')
                
db.define_table('authority',
                Field('name','string'),
                Field('uri','string'),
                Field('domain','reference domain',ondelete='NO ACTION'),
                format = '%(name)s')
                
db.define_table('term',
                Field('source_id','string'),
                Field('authority','reference authority',ondelete='NO ACTION'),
                Field('domain', 'reference domain',ondelete='NO ACTION'),
                Field('label','string'),
                Field('generated_id','string',writable=False),
                Field('comment','string'),
                format = '%(label)s')
behavior_domain_id = db(db.domain.name == 'behavior').select().first().id
behavior_domain = db(db.term.domain == behavior_domain_id)
anatomy_domain_id = db(db.domain.name == 'anatomy').select().first().id
anatomy_domain = db(db.term.domain==anatomy_domain_id)  #need to fix this
taxonomy_domain_id = db(db.domain.name == 'taxonomy').select().first().id
taxon_domain = db(db.term.domain == taxonomy_domain_id)
evidence_domain_id = db(db.domain.name == 'evidence').select().first().id
evidence_domain = db(db.term.domain == evidence_domain_id)
                
db.define_table('synonym',
		        Field('text','string'),
		        Field('term','reference term'))
		      
db.define_table('individual',
                Field('source_id','string'),
                Field('generated_id','string',writable=False))
       
db.define_table('taxon',
                Field('name','string'),
                Field('ncbi_id','string'),
                Field('ottol_id','string'),
                Field('author','string'),
                Field('year','string'),
                Field('generated_id','string',writable=False),
                format='%(name)s')
                               
db.define_table('taxonomy_authority',
                Field('name','string'),
                format='%(name)s')

db.define_table('evidence_code',
                Field('long_name','string'),
                Field('obo_id','string'),
                Field('code','string'))
                
db.define_table('participant',
                Field('taxon','reference term'),
                Field('anatomy','reference term'),
                Field('substrate','reference term',requires=IS_EMPTY_OR(IS_IN_DB(db,'term.id','%(label)s'))),
                Field('quantification','string',length=8),
                Field('label','string'),
                Field('publication_taxon','string'),
                Field('generated_id','string',writable=False))
db.participant.taxon.requires = IS_EMPTY_OR(IS_IN_DB(taxon_domain,'term.id','%(label)s'))
db.participant.anatomy.requires = IS_EMPTY_OR(IS_IN_DB(anatomy_domain,'term.id','%(label)s'))
db.participant.substrate.requires = IS_EMPTY_OR(IS_IN_DB(anatomy_domain,'term.id','%(label)s'))

db.define_table('assertion',
                Field('publication',db.publication),
                Field('publication_behavior','string'),
                Field('behavior_term','reference term'),
                Field('publication_taxon','string'),
                Field('taxon','reference taxon',requires=IS_EMPTY_OR(IS_IN_DB(db,'taxon.id','%(name)s'))),
                Field('primary_participant','reference participant',requires=IS_EMPTY_OR(IS_IN_DB(db,'participant.id','%(label)s'))),
                Field('publication_anatomy','string'),
                Field('evidence','reference evidence_code'),
                Field('generated_id','string',writable=False),
                format='Assertion: %(generated_id)s')
db.assertion.behavior_term.requires = IS_EMPTY_OR(IS_IN_DB(behavior_domain,'term.id','%(label)s'))
                                
db.define_table('assertion2term',
                Field('assertion', 'reference assertion'),
                Field('term','reference term'))
                

db.define_table('anatomy2assertion',
                Field('anatomy_term','reference anatomy_term'),
                Field('assertion','reference assertion'))

db.define_table('actor2assertion',
                Field('actorID','string'),
                Field('assertion','reference assertion'))
    
                            
db.define_table('participant2assertion',
                Field('assertion','reference assertion'),
                Field('participant', 'reference participant'),
                Field('participant_index','integer',unique=True))                                
                                                
db.define_table('ontology_source',
                 Field('name','string'),
                 Field('source_url','string'),
                 Field('processing','reference ontology_processing',requires=IS_EMPTY_OR(IS_IN_DB(db,'ontology_processing.id','%(type_name)s'))),
                 Field('last_update','datetime',writable=False),
                 Field('authority', 'reference authority'),
                 Field('domain', 'reference domain',ondelete='NO ACTION'),
                 format='Ontology: %(name)')   
                                                
db.define_table('ontology_processing',
                 Field('type_name','string'),
                 format='Ontology processing: %(type_name)')          
                                                
#########################################################################
## Define your tables below (or better in another model file) for example
##
## >>> db.define_table('mytable',Field('myfield','string'))
##
## Fields can be 'string','text','password','integer','double','boolean'
##       'date','time','datetime','blob','upload', 'reference TABLENAME'
## There is an implicit 'id integer autoincrement' field
## Consult manual for more options, validators, etc.
##
## More API examples for controllers:
##
## >>> db.mytable.insert(myfield='value')
## >>> rows=db(db.mytable.myfield=='value').select(db.mytable.ALL)
## >>> for row in rows: print row.id, row.myfield
#########################################################################

## after defining tables, uncomment below to enable auditing
# auth.enable_record_versioning(db)
