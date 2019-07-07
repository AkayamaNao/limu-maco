#基本17持に実行（UTC 8:00）

import requests
import datetime
import jpholiday

from settings import group_token

def isholiday(date):
    if date.weekday() > 4:
        return True
    elif jpholiday.is_holiday(date):
        return True
    return False

today=datetime.date.today()
tomorrow=today+datetime.timedelta(days=1)
if not isholiday(tomorrow):
    line_notify_api = 'https://notify-api.line.me/api/notify'
    group_headers = {'Authorization': 'Bearer ' + group_token}

    now=datetime.datetime.now()
    message_date = now.strftime('%Y/%m/%d %H:%M:%S')
    payload = {'message': '\n明日の注文をお願いします\nhttps://limu-maco.herokuapp.com'}
    try:
        requests.post(line_notify_api, data=payload, headers=group_headers)
        print(message_date + ' announce to group\n')
    except:
        print('Error\n', message_date)
