#!/usr/bin/env python
# encoding: utf-8
# author: Think
# created: 2018/9/20 15:34

"""
查询函数
"""

from tj.db import getSession
from tj.mapper import Lis


def getLis(barcodeId):
    session = getSession()
    try:
        return session.query(Lis).filter_by(barcodeId=barcodeId).all()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


# if __name__ == '__main__':
#     lis = getLis(300010)
#     for r in lis:
#         print(repr(r.birthday.strftime('%Y-%m-%d')))


