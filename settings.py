#https://github.com/AkayamaNao/limu-maco.git
from os import environ
from pathlib import Path
import psycopg2
import subprocess

testmode=0

DEBUG = True

SWAGGER_UI_DOC_EXPANSION = 'list'
RESTPLUS_VALIDATE = True

JSON_AS_ASCII = False

UPLOADED_CONTENT_DIR = Path("upload")

# for maco_system
update_time = 20
group_token = 'lhFEwq81neUCR4dBS3XO2d4dfLvAeLqwk63vN00fJ8n'
maco_token = 'D9mwMqqQf2dgxS9kJNbIFh0djqCT7n4ywDyHS2ZGZFS'
my_token='rL71jYoAcCK3pgRh4JmMzGVPdO8DDKd5y6gk13AVvYO'

root_password = '88248075a3514f106c0c16ee16aa06a22b56670b7b01ee56da49772218b1b289'

if testmode==1:
    group_token=my_token
    maco_token=my_token
    # maco_db = 'postgres://vojmwqggktbwcq:b68a7729d76ef371569e77a475f9aeab3ef371aa15b3ba128c3ab828cedf5bf8@ec2-54-83-201-84.compute-1.amazonaws.com:5432/ddm0m8tb2f57j8'
    maco_db = 'postgres://yezwtzucqwwbwb:101e900d0112cf656aac45392643e64a5cf159f45df42d03687d40c2c45cc4ed@ec2-23-21-160-38.compute-1.amazonaws.com:5432/d86eg6lncc5u8b'
else:
    proc = subprocess.Popen('printenv DATABASE_URL', stdout=subprocess.PIPE, shell=True)
    maco_db = proc.stdout.read().decode('utf-8').strip()

#SQLALCHEMY_DATABASE_URI = 'postgres://{user}:{password}@{host}/{database}'.format(**dbconf.maco_db)
SQLALCHEMY_DATABASE_URI = maco_db
SQLALCHEMY_TRACK_MODIFICATIONS = True