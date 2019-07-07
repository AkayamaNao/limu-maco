from datetime import datetime
from flask_sqlalchemy import SQLAlchemy as SA


class SQLAlchemy(SA):
    def apply_pool_defaults(self, app, options):
        SA.apply_pool_defaults(self, app, options)
        options["pool_pre_ping"] = True


db = SQLAlchemy()


def now():
    return datetime.now().timestamp()


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.String(63), nullable=False, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    option = db.Column(db.Integer, nullable=False, default=0)

    def __init__(self, user_id, user_name, option):
        self.id = user_id
        self.name = user_name
        self.option = option


class Order(db.Model):
    __tablename__ = 'order'
    date = db.Column(db.Integer, nullable=False, primary_key=True)
    user_id = db.Column(db.String(63), nullable=False, primary_key=True)
    order_num = db.Column(db.Integer, nullable=False)
    collected = db.Column(db.Integer, nullable=False, default=0)
    created_at = db.Column(db.Integer, nullable=False, default=now)

    def __init__(self, date, user_id, order_num):
        self.date = date
        self.user_id = user_id
        self.order_num = order_num


class Delivery(db.Model):
    __tablename__ = 'delivery'
    date = db.Column(db.Integer, nullable=False, primary_key=True)
    user_id = db.Column(db.String(63), nullable=False)
    collected = db.Column(db.Integer, nullable=False, default=0)
    created_at = db.Column(db.Integer, nullable=False, default=now)

    def __init__(self, date, user_id):
        self.date = date
        self.user_id = user_id


class Menu(db.Model):
    __tablename__ = 'menu'
    date = db.Column(db.Integer, nullable=False, primary_key=True)
    user_id = db.Column(db.String(63), nullable=False)
    menu1 = db.Column(db.Text, nullable=False)
    menu2 = db.Column(db.Text, nullable=False)
    menu3 = db.Column(db.Text, nullable=False)
    finish = db.Column(db.Integer, nullable=False, default=0)
    created_at = db.Column(db.Integer, nullable=False, default=now)

    def __init__(self, date, user_id, menu1, menu2, menu3):
        self.date = date
        self.user_id = user_id
        self.menu1 = menu1
        self.menu2 = menu2
        self.menu3 = menu3


class Points(db.Model):
    __tablename__ = 'points'
    month = db.Column(db.Integer, nullable=False, primary_key=True)
    user_id = db.Column(db.String(63), nullable=False, primary_key=True)
    point = db.Column(db.Integer, nullable=False, default=0)
    bonus=db.Column(db.Integer, nullable=False, default=0)
    collected = db.Column(db.Integer, nullable=False, default=0)
    created_at = db.Column(db.Integer, nullable=False, default=now)

    def __init__(self, month, user_id, point,bonus):
        self.month = month
        self.user_id = user_id
        self.point = point
        self.bonus=bonus
