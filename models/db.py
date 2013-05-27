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
                                
db.define_table('taxon',
                Field('name','string'),
                Field('ncbi_id','string'),
                Field('ottol_id','string'),
                Field('author','string'),
                Field('year','string'))
               
db.define_table('synonym',
                Field('name','string'),
                Field('author','string'),
                Field('year','string'),
                Field('valid_name',db.taxon,ondelete='NO ACTION',requires=IS_EMPTY_OR(IS_IN_DB(db,'taxon.id', '%(name)s'))))

db.define_table('term_usage',
                Field('behavior_term','string'),
                Field('publication_taxon','string'),
                Field('direct_source',db.publication,ondelete='NO ACTION',requires=IS_EMPTY_OR(IS_IN_DB(db, 'publication.id', '%(author_list)s %(publication_year)s'))),
                Field('evidence','string'),
                Field('secondary_source',db.publication,ondelete='NO ACTION',requires=IS_EMPTY_OR(IS_IN_DB(db, 'publication.id', '%(author_list)s %(publication_year)s'))),
                ##Field('resolved_taxon_name','string'),
                Field('anatomy','string'),
                Field('participant_list','string'),
                Field('obo_term_name','string'),
                Field('obo_term_id','string'),
                Field('nbo_term_name','string'),
                Field('nbo_term_id','string'),
                Field('abo_term','string'),
                Field('description','text'),
                Field('resolved_taxon_id',db.taxon,ondelete='NO ACTION',requires=IS_EMPTY_OR(IS_IN_DB(db,'taxon.id', '%(name)s'))))
                
                                                
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
