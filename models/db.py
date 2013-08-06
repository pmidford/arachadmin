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
                format = '%(author)s (%(publication_year)s)')
                                
db.define_table('taxon',
                Field('name','string'),
                Field('ncbi_id','string'),
                Field('ottol_id','string'),
                Field('author','string'),
                Field('year','string'),
                Field('generated_id','string',writable=False),
                format='%(name)s')
               
db.define_table('taxon_synonym',
                Field('name','string'),
                Field('author','string'),
                Field('year','string'),
                Field('valid_name','reference taxon',ondelete='NO ACTION'), 
                format='%(name) (synonym)')

db.define_table('anatomy_term',
                Field('name','string'),
                Field('spd_id','string'),
                Field('obo_id','string'),
                Field('generated_id','string',writable=False),
                format='%(name)',
                migrate=True)                

db.define_table('behavior_term',
                Field('name','string'),
                Field('nbo_id','string'),
                Field('obo_id','string'),
                Field('abo_id','string'),
                Field('generated_id','string',writable=False),
                format='%(name)')                

db.define_table('behavior_synonym',
                Field('name','string'),
                Field('primary_term',db.behavior_term,ondelete='NO ACTION',requires=IS_EMPTY_OR(IS_IN_DB(db,'taxon.id','%(name)s'))),
                format='%(name) (synonym)')

db.define_table('evidence_code',
                Field('long_name','string'),
                Field('obo_id','string'),
                Field('code','string'))

db.define_table('assertion',
                Field('publication',db.publication),
                Field('publication_behavior','string'),
                Field('behavior_term','integer'),
                Field('publication_taxon','string'),
                Field('taxon','reference taxon',requires=IS_EMPTY_OR(IS_IN_DB(db,'taxon.id','%(name)s'))),
                Field('publication_anatomy','string'),
                Field('evidence','integer'),
                Field('generated_id','string',writable=False),
                format='[Assertion]%(generated_id)')
                
                
db.define_table('behavior2assertion',
                Field('behavior','reference behavior_term'),
                Field('assertion','reference assertion'))

db.define_table('anatomy2assertion',
                Field('anatomy_term','reference anatomy_term'),
                Field('assertion','reference assertion'))

db.define_table('actor2assertion',
                Field('actorID','string'),
                Field('assertion','reference assertion'))
    
                            
db.define_table('participant2assertion',
                Field('participantclass','reference taxon'),
                Field('participantID','string'),
                Field('assertion','reference assertion'))
                                                
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
