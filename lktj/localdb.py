#!/usr/bin/env python
# encoding: utf-8
# author: Think
# created: 2018/10/13 9:09

"""
  本地的sqlite3数据库，统计数据用
"""

import os
from datetime import datetime
from sqlalchemy import create_engine, Column, String, Text, Integer, DateTime, Boolean, Date
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base

_basedir = ''


def _getDataFile():
    datapath = os.path.join(_basedir, 'data')

    if not os.path.exists(datapath):
        os.mkdir(datapath)

    return os.path.join(datapath, 'data.sqlite3')


def _getEngine():
    # 创建数据库实例
    return create_engine('sqlite:///{}'.format(_getDataFile()), echo=False)


def _getSession():
    # 创建连接
    Session_class = sessionmaker(bind=_getEngine())

    Session = scoped_session(Session_class())

    return Session()


# 定义数据表
Base = declarative_base()


class TransLog(Base):
    __tablename__ = 'translog'
    id = Column(Integer, autoincrement="auto", primary_key=True)
    order_id = Column(String(30), nullable=False, index=True)
    username = Column(String(30))
    sex_name = Column(String(2))
    age = Column(String(3))
    birth = Column(Date)
    main_check_date = Column(DateTime)
    arrival_date = Column(DateTime)
    is_successfull = Column(Boolean, nullable=False)
    trans_msg = Column(Text)
    trans_date = Column(Date, nullable=False, index=True, default=datetime.now())
    trans_time = Column(DateTime, nullable=False, default=datetime.now())


class Orders(Base):
    __tablename__ = 'orders'
    order_id = Column(String(30), primary_key=True)
    username = Column(String(30))
    sex_name = Column(String(2))
    age = Column(String(3))
    birth = Column(Date)
    main_check_date = Column(DateTime)
    arrival_date = Column(DateTime)
    trans_date = Column(Date, nullable=False, index=True, default=datetime.now())
    trans_time = Column(DateTime, nullable=False, default=datetime.now())


def initdb(dbpath=None):
    # 初始化数据库
    global _basedir
    _basedir = dbpath
    Base.metadata.create_all(_getEngine())


def saveTransLog(translog):
    session = _getSession()
    try:
        session.add(translog)

        if translog.is_successfull:
            orders = session.query(Orders).get(translog.order_id)
            if orders:
                orders.username = translog.username
                orders.sex_name = translog.sex_name
                orders.age = translog.age
                orders.birth = translog.birth
                orders.arrival_date = translog.arrival_date
                orders.main_check_date = translog.main_check_date
                orders.trans_date = translog.trans_date
                orders.trans_time = translog.trans_time
                session.merge(orders)
            else:
                orders = Orders(order_id=translog.order_id,
                                username=translog.username,
                                sex_name=translog.sex_name,
                                age=translog.age,
                                birth=translog.birth,
                                main_check_date=translog.main_check_date,
                                arrival_date=translog.arrival_date
                                )
                session.add(orders)
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


def isInOrders(order_id):
    session = _getSession()
    try:
        return session.query(Orders).get(order_id) != None
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

# if __name__ == '__main__':
#    initdb()
#    log = TransLog(order_id=10010,username='张忠文',is_successfull=True)
#    saveTransLog(log)
