#基本20持に実行(UTC 11:00)

import requests
import datetime
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import random
import numpy as np
import pandas as pd

from settings import *
import models

line_notify_api = 'https://notify-api.line.me/api/notify'
maco_headers = {'Authorization': 'Bearer ' + maco_token}
group_headers = {'Authorization': 'Bearer ' + group_token}

maco = create_engine(maco_db,pool_pre_ping=True)
Session = sessionmaker(bind=maco)
s = Session()

now=datetime.datetime.now()
month = now.strftime('%Y%m')
message_date = now.strftime('%Y/%m/%d %H:%M:%S')
tomorrow=now+datetime.timedelta(days=1)
menu = s.query(models.Menu).filter_by(finish=0,date=int(tomorrow.strftime('%Y%m%d'))).first()
if menu is not None:
    menulist = [menu.menu1, menu.menu2, menu.menu3]
    date = menu.date
    query = f'''select user_id,name,order_num,option from ( select * from "order" where date = {date} and 
                order_num != 0 ) as a inner join "user" on a.user_id = "user".id;'''
    df = pd.read_sql(query, maco)
    if len(df)>0:
        ordersum = [sum(df['order_num']==1), sum(df['order_num']==2), sum(df['order_num']==3)]

        # send maco
        message = ''
        for i in range(len(menulist)):
            if ordersum[i] > 0:
                message = message + f'{menulist[i]}\t{ordersum[i]}個\n'
        payload = {'message': '\n' + message + 'お願いします'}
        try:
            requests.post(line_notify_api, data=payload, headers=maco_headers)
            print(message_date + ' order was sended to maco\n')
        except:
            print('Error\n',message_date, message)

        #send group
        dlist=df[df['option'] == 0]
        if len(dlist)<1:
            dlist=df
        dlist=dlist.reset_index()

        query = f'''select o_date as date, "order", delivery from (select date as o_date,user_id as order from 
                "order" where order_num != 0 and date between {month}00 and {month}99 order by o_date) as a left 
                outer join (select date as d_date,user_id as delivery from "delivery" where date between 
                {month}00 and {month}99) as b on a.o_date = b.d_date;'''
        df2 = pd.read_sql(query, maco)
        cost=[]
        for index,row in dlist.iterrows():
            onum=sum(df2['order'] == row['user_id'])
            dnum=sum(df2['delivery'] == row['user_id'])
            cost.append(onum-dnum)
        cost=np.array(cost) - min(cost)
        if sum(cost) < 1:
            cost = cost + 1
        randlist = [i for i in range(len(cost)) for j in range(cost[i])]
        random.seed(datetime.datetime.now().timestamp())
        print(randlist)
        deli = dlist.loc[random.choice(randlist)]

        s.add(models.Delivery(date, deli['user_id']))
        s.commit()
        message=''
        for i in range(len(menulist)):
            if ordersum[i] > 0:
                tmp=','.join(df[df['order_num'] == i+1]['name'])
                message = message + f'\n{menulist[i]}\t{ordersum[i]}個({tmp})'
        group_payload = {'message': f'\n明日の配達は{deli["name"]}です\n{message}'}
        try:
            requests.post(line_notify_api, data=group_payload, headers=group_headers)
            print(message_date + ' delivery was sended to group\n')
        except:
            print('Error\n', message_date, message)
    else:
        print(message_date + ' order is none\n')
    menu.finish=1
    s.commit()
else:
    print(message_date + ' menu is none\n')



    # order = s.query(models.Order).filter_by(date=date).all()
    # if len(order) > 0:
    #     #send maco
    #     orderlist = []
    #     ordersum = [0, 0, 0]
    #     for row in order:
    #         if row.order_num < 1:
    #             continue
    #         tmp = s.query(models.User).filter_by(id=row.user_id).first()
    #         num = row.order_num - 1
    #         orderlist.append([tmp.name, menulist[num], tmp.option, tmp.id])
    #         ordersum[num] = ordersum[num] + 1
    #     message = ''
    #     for i in range(len(menulist)):
    #         if ordersum[i] > 0:
    #             message = message + f'{menulist[i]}\t{ordersum[i]}つ\n'
    #     payload = {'message': '\n' + message + 'お願いします'}
    #     try:
    #         requests.post(line_notify_api, data=payload, headers=maco_headers)
    #         print(message_date + ' order is sended to maco\n')
    #     except:
    #         print('Error\n',message_date, message)

    #     #send group
    #     member = []
    #     for row in orderlist:
    #         if row[2] != 1:
    #             member.append([row[0], row[3]])
    #     if len(member) < 1:
    #         for row in orderlist:
    #             member.append([row[0], row[3]])
    #     random.seed(datetime.datetime.now().timestamp())
    #     deli = member[random.randrange(len(member))]
    #     s.add(models.Delivery(date, deli[1]))
    #     s.commit()
    #     group_payload = {'message': '\n' + message + f'\n明日の配達は{deli[0]}です'}
    #     try:
    #         requests.post(line_notify_api, data=group_payload, headers=group_headers)
    #         print(message_date + ' delivery is sended to group\n')
    #     except:
    #         print('Error\n', message_date, message)
    # else:
    #     print(message_date + ' order is none\n')
    # menu.finish=1
    # s.commit()

#culculate point
if tomorrow.day == 1:
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