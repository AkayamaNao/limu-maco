#基本20持に実行(UTC 11:00)

import requests
import datetime
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import random

from settings import maco_token,group_token
import dbconf
import models

line_notify_api = 'https://notify-api.line.me/api/notify'
maco_headers = {'Authorization': 'Bearer ' + maco_token}
group_headers = {'Authorization': 'Bearer ' + group_token}

#maco_db = create_engine('postgres://{user}:{password}@{host}/{database}'.format(**dbconf.maco_db),pool_pre_ping=True)
maco_db = create_engine(dbconf.maco_db,pool_pre_ping=True)
Session = sessionmaker(bind=maco_db)
s = Session()

now=datetime.datetime.now()
message_date = now.strftime('%Y/%m/%d %H:%M:%S')
tomorrow=now+datetime.timedelta(days=1)
tomorrow_str=tomorrow.strftime('%Y%m%d')
menu = s.query(models.Menu).filter_by(finish=0,date=int(tomorrow_str)).first()
if menu is not None:
    menulist = [menu.menu1, menu.menu2, menu.menu3]
    date = menu.date
    order = s.query(models.Order).filter_by(date=date).all()
    if len(order) > 0:
        #send maco
        orderlist = []
        ordersum = [0, 0, 0]
        for row in order:
            if row.order_num < 1:
                continue
            tmp = s.query(models.User).filter_by(id=row.user_id).first()
            num = row.order_num - 1
            orderlist.append([tmp.name, menulist[num], tmp.option, tmp.id])
            ordersum[num] = ordersum[num] + 1
        message = ''
        for i in range(len(menulist)):
            if ordersum[i] > 0:
                message = message + f'{menulist[i]}\t{ordersum[i]}つ\n'
        payload = {'message': '\n' + message + 'お願いします'}
        try:
            requests.post(line_notify_api, data=payload, headers=maco_headers)
            print(message_date + ' order is sended to maco\n')
        except:
            print('Error\n',message_date, message)

        #send group
        member = []
        for row in orderlist:
            if row[2] != 1:
                member.append([row[0], row[3]])
        if len(member) < 1:
            for row in orderlist:
                member.append([row[0], row[3]])
        random.seed(datetime.datetime.now().timestamp())
        deli = member[random.randrange(len(member))]
        # s.add(models.Delivery(date, deli[1]))
        # s.commit()
        group_payload = {'message': '\n' + message + f'\n明日の配達は{deli[0]}です'}
        try:
            requests.post(line_notify_api, data=group_payload, headers=group_headers)
            print(message_date + ' delivery is sended to group\n')
        except:
            print('Error\n', message_date, message)
    else:
        print(message_date + ' order is none\n')
    # menu.finish=1
    # s.commit()
else:
    print(message_date + ' menu is none\n')
