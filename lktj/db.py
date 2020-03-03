#!/usr/bin/env python
# encoding: utf-8
# author: Think
# created: 2018/9/20 14:56

"""
mysql数据库连接
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session


#定义数据库常量
USERNAME_CONST = "lkhnjk"
PASSWORD_CONST = "lkhnjk!QAZ"
HOST_CONST = "192.168.75.11"
DATABASE_CONST = "jk"
CONN_CONST = "mysql+pymysql://%s:%s@%s/%s" % (USERNAME_CONST, PASSWORD_CONST, HOST_CONST, DATABASE_CONST)

# 创建数据库实例
engine = create_engine(CONN_CONST,
                       encoding='utf-8',
                       echo=False,
                       pool_size=5,
                       # pool_recycle=5,
                       )

#创建连接
Session_class = sessionmaker(bind=engine)
Session = scoped_session(Session_class)


def getSession():
   return Session()