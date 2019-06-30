from os import environ
from pathlib import Path
import psycopg2

import dbconf

DEBUG = True

SWAGGER_UI_DOC_EXPANSION = 'list'
RESTPLUS_VALIDATE = True

SQLALCHEMY_DATABASE_URI = dbconf.maco_db
SQLALCHEMY_TRACK_MODIFICATIONS = True

JSON_AS_ASCII = False

UPLOADED_CONTENT_DIR = Path("upload")

# for maco_system
update_time = 20
group_token = 'lhFEwq81neUCR4dBS3XO2d4dfLvAeLqwk63vN00fJ8n'
maco_token = 'D9mwMqqQf2dgxS9kJNbIFh0djqCT7n4ywDyHS2ZGZFS'
my_token='rL71jYoAcCK3pgRh4JmMzGVPdO8DDKd5y6gk13AVvYO'
#group_token=my_token
#maco_token=my_token
root_password = '88248075a3514f106c0c16ee16aa06a22b56670b7b01ee56da49772218b1b289'
