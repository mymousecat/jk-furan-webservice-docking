#!/usr/bin/env python
# encoding: utf-8
# author: Think
# created: 2018/9/20 15:34

"""
查询函数
"""

from lktj.db import getSession
from lktj.mapper import BaseInfo, Fare, Recheck, Results


def getBaseInfo(mainCheckDate):
    """
    根据总检时间查询返回的人员基本信息
    :param mainCheckDate:
    :return:
    """
    session = getSession()

    try:
        return session.query(BaseInfo).filter(BaseInfo.arrival_date > mainCheckDate).first()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


def getBaseInfoByOrderId(order_id):
    session = getSession()
    try:
        return session.query(BaseInfo).get(order_id)
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


def getFare(order_id):
    session = getSession()
    try:
        return session.query(Fare).filter(Fare.order_id == order_id).all()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


def getRecheck(order_id):
    session = getSession()
    try:
        return session.query(Recheck).filter(Recheck.order_id == order_id).all()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


def getResults(order_id):
    session = getSession()
    try:
        return session.query(Results).filter(Results.order_id == order_id).all()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


if __name__ == '__main__':
    baseinfo = getBaseInfo('1970-01-01')
    print(type(baseinfo.arrival_date))
