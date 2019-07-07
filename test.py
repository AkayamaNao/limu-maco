import requests
import datetime
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import random
import pandas as pd
from settings import *
import models
import numpy as np

maco_db = 'postgres://vojmwqggktbwcq:b68a7729d76ef371569e77a475f9aeab3ef371aa15b3ba128c3ab828cedf5bf8@ec2-54-83-201-84.compute-1.amazonaws.com:5432/ddm0m8tb2f57j8'
maco = create_engine(maco_db, pool_pre_ping=True)
Session = sessionmaker(bind=maco)
s = Session()

now = datetime.datetime.now()
tomorrow = now + +datetime.timedelta(days=1)
if tomorrow.day == 1:
    month = now.strftime('%Y%m')
    query = f'''select user_id,name,point from (select user_id, sum(mcount) as point from (select user_id, count(user_id)
            as mcount from menu where date between {month}00 and {month}99 group by user_id union select user_id,
            count(user_id)*2 as dcount from delivery where date between {month}00 and {month}99 group by user_id)
            as total group by user_id) as points inner join "user" on  points.user_id = "user".id order by point desc;
            '''
    df = pd.read_sql(query, maco)
    query = f'''select count(*) from ( select user_id from "order" where date between {month}00 and {month}99 and 
            order_num != 0 ) as a inner join ( select id from "user" where option = 1 ) as b on a.user_id = b.id;'''
    num = pd.read_sql(query, maco).values[0][0]

    bonus_list = np.zeros(len(df))
    rank = df[0:3]['point']
    if len(df) > 2:
        if rank[0] == rank[1] and rank[1] == rank[2]:
            tmp = int(np.floor(num / 3))
            bonus_list[0] = tmp
            bonus_list[1] = tmp
            bonus_list[2] = tmp
        elif rank[0] == rank[1]:
            tmp = int(np.floor(num / 5))
            bonus_list[2] = tmp
            tmp = int(np.floor((num - tmp) / 2))
            bonus_list[0] = tmp
            bonus_list[1] = tmp
        elif rank[1] == rank[2]:
            tmp = int(np.floor(num / 2))
            bonus_list[0] = tmp
            tmp = int(np.floor((num - tmp) / 2))
            bonus_list[1] = tmp
            bonus_list[2] = tmp
        else:
            bonus_list[0] = int(np.ceil(num / 2))
            bonus_list[1] = int(np.ceil((num - bonus_list[0]) * 3 / 5))
            bonus_list[2] = int(num - bonus_list[0] - bonus_list[1])
    elif len(df) == 2:
        if rank[0] == rank[1]:
            tmp = int(np.floor(num / 2))
            bonus_list[0] = tmp
            bonus_list[1] = tmp
        else:
            bonus_list[0] = int(np.ceil(num * 7 / 10))
            bonus_list[1] = num - bonus_list[0]
    elif len(df)==1:
        bonus_list[0] = num

    for index, row in df.iterrows():
        s.add(models.Points(int(month), row['user_id'], int(row['point']), int(bonus_list[index]*50)))
        print(int(month), row['user_id'], int(row['point']), int(bonus_list[index]*50))
    s.commit()
