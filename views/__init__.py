# coding:utf8
from flask import Blueprint, current_app, redirect, render_template, request, session, url_for
from sqlalchemy import create_engine, distinct
from sqlalchemy.orm import sessionmaker
import re
import datetime
import psycopg2

import dbconf
import models
import settings

blueprint = Blueprint('view', __name__, static_folder='static')

#maco_db = create_engine('postgres://{user}:{password}@{host}/{database}'.format(**dbconf.maco_db), pool_pre_ping=True)
maco_db = create_engine(dbconf.maco_db, pool_pre_ping=True)

root_password = settings.root_password
update_time = settings.update_time

symbolReg = re.compile(r'^[a-zA-Z0-9!-/:-@[-`{-~]+$')


def isnotsymbol(s):
    return symbolReg.match(s) is None


def update_date():
    now = datetime.datetime.now()
    update = now + datetime.timedelta(hours=24 - update_time)
    return int(update.strftime("%Y%m%d"))


def next_date():
    now = datetime.datetime.now()
    nextdate = now + datetime.timedelta(hours=24 - update_time) + datetime.timedelta(days=1)
    return int(nextdate.strftime("%Y%m%d"))


weekstr = ['月', '火', '水', '木', '金', '土', '日']


@blueprint.route('/', methods=['GET', 'POST'])
def index():
    # login session
    if 'user_id' not in session:
        return redirect(url_for('view.login'))
    user_id = session['user_id']
    Session = sessionmaker(bind=maco_db)
    s = Session()
    user = s.query(models.User).filter_by(id=user_id).first()
    if user is None:
        current_app.logger.error(f'Unexpected error: {user_id} is not found in DB')
        return redirect(url_for('view.login'))

    menu = s.query(models.Menu).filter_by(finish=0).first()
    if menu is None:
        return redirect(url_for('view.addmenu'))

    menulist = [menu.menu1, menu.menu2, menu.menu3]
    date = menu.date

    if request.method == 'POST':
        order_num = int(request.form['menunum'])
        tmp = s.query(models.Order).filter_by(date=date, user_id=user_id).first()
        if tmp is None:
            s.add(models.Order(date, user_id, order_num))
        else:
            tmp.order_num = order_num
        s.commit()

    tmp = s.query(models.Order).filter_by(date=date, user_id=user_id).first()
    if tmp is None:
        myorder = 0
    else:
        myorder = tmp.order_num

    order = s.query(models.Order).filter_by(date=date).all()
    orderlist = []
    ordersum = [0, 0, 0]
    for row in order:
        if row.order_num < 1:
            continue
        tmp = s.query(models.User).filter_by(id=row.user_id).first()
        num = row.order_num - 1
        orderlist.append([tmp.name, menulist[num]])
        ordersum[num] = ordersum[num] + 1

    message = ''
    for i in range(len(menulist)):
        if ordersum[i] > 0:
            message = message + f'{menulist[i]}\t{ordersum[i]}つ\n'
    if message != '':
        message = message + 'お願いします'

    dt = datetime.datetime.strptime(str(date), '%Y%m%d')
    month = int(dt.strftime('%m'))
    day = int(dt.strftime('%d'))
    week = int(dt.strftime('%j')) - int(dt.strftime('%W')) * 7
    date = f'{month}月{day}日({weekstr[week]}) '

    return render_template('index.html', date=date, menu=menulist, myorder=myorder, order=orderlist, message=message)


@blueprint.route('/addmenu', methods=["GET", "POST"])
def addmenu():
    # login session
    if 'user_id' not in session:
        return redirect(url_for('view.login'))
    user_id = session['user_id']
    Session = sessionmaker(bind=maco_db)
    s = Session()
    user = s.query(models.User).filter_by(id=user_id).first()
    if user is None:
        current_app.logger.error(f'Unexpected error: {user_id} is not found in DB')
        return redirect(url_for('view.login'))

    if request.method == 'POST':
        current_app.logger.info(f'Requested form {request.form}')
        date = request.form['dateinfo']
        menu1 = request.form['menu1']
        menu2 = request.form['menu2']
        menu3 = request.form['menu3']
        try:
            date = int(date)
        except:
            return render_template('addmenu.html', error='日付が正しくありません')
        if date <= update_date():
            return render_template('addmenu.html', error='日付が正しくありません')
        user_id = session['user_id']
        try:
            s.add(models.Menu(date, user_id, menu1, menu2, menu3))
            s.commit()
        except:
            return render_template('addmenu.html', error='日付が正しくありません')
        return redirect(url_for('view.index'))
    return render_template('addmenu.html', date=next_date())


@blueprint.route('/editmenu', methods=["GET", "POST"])
def editmenu():
    # login session
    if 'user_id' not in session:
        return redirect(url_for('view.login'))
    user_id = session['user_id']
    Session = sessionmaker(bind=maco_db)
    s = Session()
    user = s.query(models.User).filter_by(id=user_id).first()
    if user is None:
        current_app.logger.error(f'Unexpected error: {user_id} is not found in DB')
        return redirect(url_for('view.login'))

    if request.method == 'GET':
        menu = s.query(models.Menu).filter(models.Menu.date > update_date()).first()
        if menu is None:
            return redirect(url_for('view.addmenu'))

        menulist = [menu.menu1, menu.menu2, menu.menu3]
        date = menu.date
        return render_template('editmenu.html', date=date, menu=menulist)

    if request.method == 'POST':
        current_app.logger.info(f'Requested form {request.form}')
        date = request.form['dateinfo']
        menu1 = request.form['menu1']
        menu2 = request.form['menu2']
        menu3 = request.form['menu3']
        try:
            date = int(date)
        except:
            return render_template('editmenu.html', date=date, menu=[menu1, menu2, menu3], error='日付が正しくありません')
        if date <= update_date():
            return render_template('editmenu.html', date=date, menu=[menu1, menu2, menu3], error='日付が正しくありません')
        user_id = session['user_id']
        menu = s.query(models.Menu).filter(models.Menu.date > update_date()).first()
        menu.date = date
        menu.menu1 = menu1
        menu.menu2 = menu2
        menu.menu3 = menu3
        # menu.user_id=user_id
        try:
            s.commit()
        except:
            return render_template('editmenu.html', date=date, menu=[menu1, menu2, menu3], error='日付が正しくありません')
        return redirect(url_for('view.index'))


@blueprint.route('/data', methods=["GET"])
def data():
    # login session
    if 'user_id' not in session:
        return redirect(url_for('view.login'))
    user_id = session['user_id']
    Session = sessionmaker(bind=maco_db)
    s = Session()
    user = s.query(models.User).filter_by(id=user_id).first()
    if user is None and user_id!='root':
        current_app.logger.error(f'Unexpected error: {user_id} is not found in DB')
        return redirect(url_for('view.login'))

    menu = s.query(models.Menu).filter(models.Menu.date > update_date() - 30).all()
    data = []
    for row in menu:
        data.append(row.date)
    data.reverse()
    return render_template('data.html', data=data)


@blueprint.route('/data/<int:date>', methods=["GET"])
def data2(date):
    # login session
    if 'user_id' not in session:
        return redirect(url_for('view.login'))
    user_id = session['user_id']
    Session = sessionmaker(bind=maco_db)
    s = Session()
    user = s.query(models.User).filter_by(id=user_id).first()
    if user is None and user_id!='root':
        current_app.logger.error(f'Unexpected error: {user_id} is not found in DB')
        return redirect(url_for('view.login'))

    menu = s.query(models.Menu).filter_by(date=date).first()
    menulist = [menu.menu1, menu.menu2, menu.menu3]

    order = s.query(models.Order).filter_by(date=date).all()
    orderlist = []
    for row in order:
        if row.order_num < 1:
            continue
        tmp = s.query(models.User).filter_by(id=row.user_id).first()
        num = row.order_num - 1
        orderlist.append([tmp.name, menulist[num]])

    tmp = s.query(models.Delivery).filter_by(date=date).first()
    if tmp is not None:
        delivery = s.query(models.User).filter_by(id=tmp.user_id).first()
        return render_template('data2.html', data=orderlist, delivery=delivery.name)
    else:
        return render_template('data2.html', data=orderlist)


@blueprint.route('/collect', methods=["GET"])
def collect():
    # login session
    if 'user_id' not in session:
        return redirect(url_for('view.login'))
    user_id = session['user_id']
    if user_id != 'root':
        return redirect(url_for('view.login'))

    Session = sessionmaker(bind=maco_db)
    s = Session()
    order = s.query(distinct(models.Order.user_id)).filter_by(collected=0).filter(models.Order.order_num != 0,
                                                                                  models.Order.date <= update_date()).all()
    # delivery = s.query(distinct(models.Delivery.user_id)).filter_by(collected=0).all()
    orderlist = []
    for row in order:
        user_id = row[0]
        user = s.query(models.User).filter_by(id=user_id).first()
        orderlist.append([user_id, user.name])

    return render_template('collect.html', data=orderlist)


@blueprint.route('/collect/<string:target_user_id>', methods=["GET", "POST"])
def collect2(target_user_id):
    # login session
    if 'user_id' not in session:
        return redirect(url_for('view.login'))
    user_id = session['user_id']
    if user_id != 'root':
        return redirect(url_for('view.login'))

    Session = sessionmaker(bind=maco_db)
    s = Session()
    if request.method == 'GET':
        option = s.query(models.User.option).filter_by(id=target_user_id).first()
        if option[0] == 1:
            fee = 350
        else:
            fee = 300

        data = []
        total = 0
        order = s.query(models.Order.date).filter_by(collected=0, user_id=target_user_id).filter(
            models.Order.order_num != 0, models.Order.date <= update_date()).all()
        for row in order:
            data.append([str(row[0]) + ' 弁当', str(fee)])
            total = total + fee

        delivery = s.query(models.Delivery.date).filter_by(collected=0, user_id=target_user_id).all()
        for row in delivery:
            date = row[0]
            tmp = s.query(models.Order).filter_by(date=date).filter(models.Order.order_num != 0).all()
            num = len(tmp)
            data.append([str(date) + ' 配達', '-' + str(300 * num)])
            total = total - 300 * num

        return render_template('collect2.html', data=data, total=total)
    else:
        order = s.query(models.Order).filter_by(collected=0, user_id=target_user_id).filter(models.Order.order_num != 0,
                                                                                            models.Order.date <= update_date()).all()
        delivery = s.query(models.Delivery).filter_by(collected=0, user_id=target_user_id).all()
        for row in order:
            row.collected = 1
        for row in delivery:
            row.collected = 1
        s.commit()
        return redirect(url_for('view.collect'))


@blueprint.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        current_app.logger.info(f'Requested form {request.form}')
        user_id = request.form['user_id']

        if user_id == 'root':
            return redirect(url_for('view.root'))

        Session = sessionmaker(bind=maco_db)
        s = Session()
        result = s.query(models.User).filter_by(id=user_id).first()
        if result:
            current_app.logger.info(f'User {user_id} logged in successfully.')
            session['user_id'] = user_id
            current_app.logger.debug(session)
            return redirect(url_for('view.index'))
        else:
            current_app.logger.info('Wrong ID')
            return render_template('login.html', error='そのIDは存在しません')
    return render_template('login.html')


@blueprint.route('/root', methods=['GET', 'POST'])
def root():
    if request.method == 'POST':
        current_app.logger.info(f'Requested form {request.form}')
        hashed_password = request.form['hashed_password']
        if hashed_password == root_password:
            current_app.logger.info(f'User root logged in successfully.')
            session['user_id'] = 'root'
            current_app.logger.debug(session)
            return redirect(url_for('view.collect'))
        else:
            current_app.logger.info('Wrong password')
            return redirect(url_for('view.login'))
    return render_template('root.html')


@blueprint.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('view.index'))


@blueprint.route('/addaccount', methods=['GET', 'POST'])
def account():
    if request.method == 'POST':
        user_id = request.form['user_id']
        name = request.form['name']
        try:
            option = request.form['option']
            option = int(option)
        except:
            option = 0
        if len(user_id) * len(name) < 1:
            return render_template('addaccount.html', error=u'すべて入力してください')
        if user_id=='root':
            return render_template('addaccount.html', error=u'そのIDは使用できません')
        if isnotsymbol(user_id):
            return render_template('addaccount.html', error=u'IDは半角でお願いします')
        try:
            name.encode('cp932')
        except:
            return render_template('addaccount.html', error=u'その名前は使えません')
        Session = sessionmaker(bind=maco_db)
        s = Session()
        tmp = s.query(models.User).filter_by(id=user_id).first()
        if tmp is not None:
            return render_template('addaccount.html', error=u'そのIDは既に使われています')
        s.add(models.User(user_id, name, option))
        s.commit()
        current_app.logger.info(f'User {user_id} logged in successfully.')
        session['user_id'] = user_id
        return redirect(url_for('view.index'))
    else:
        return render_template('addaccount.html')
