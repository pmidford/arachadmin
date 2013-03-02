import datetime, socket, os, sys
from ConfigParser import SafeConfigParser

defaults = dict(host="localhost", user="arachnolingua", password="inukumo", dbname="arachadmin")

#conf = SafeConfigParser(defaults)

#user = password = dbname = host = ''
user="arachnolingua"
password="inukumo"
dbname="arachadmin"
host="localhost"

#db = DAL('sqlite://storage.sqlite',pool_size=1,check_reserved=['all'])
db = DAL("mysql://%s:%s@%s/%s" % (user, password, host, dbname), migrate=True ) 

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
                format='%(author_list)s %(publication_year)s')
                
db.define_table('term_usage',
                Field('behavior_term','string'),
                Field('publication_taxon','string'),
                Field('direct_source',db.publication,ondelete='NO ACTION',requires=IS_EMPTY_OR(IS_IN_DB(db, 'publication.id', '%(author_list)s %(publication_year)s'))),
                Field('evidence','string'),
                Field('secondary_source',db.publication,ondelete='NO ACTION',requires=IS_EMPTY_OR(IS_IN_DB(db, 'publication.id', '%(author_list)s %(publication_year)s'))),
                Field('resolved_taxon','string'),
                Field('anatomy','string'),
                Field('participant_list','string'),
                Field('obo_term_name','string'),
                Field('obo_term_id','string'),
                Field('nbo_term_name','string'),
                Field('nbo_term_id','string'),
                Field('abo_term','string'),
                Field('description','text'))
                
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
