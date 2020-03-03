#!/usr/bin/env python
# encoding: utf-8
# author: Think
# created: 2018/10/12 17:09

"""
  保存和取回持久化的日期参数
"""



# def initBeginTime(beginTime):
#     global _beginTime



import os,pickle
from datetime import datetime

_basedir = ''

_beginTime = ''


def _getDataFile():
    datapath = os.path.join(_basedir, 'data')

    if not os.path.exists(datapath):
        os.mkdir(datapath)

    return os.path.join(datapath, 'mainchecktime.data')


def initDataPath(datapath,beginTime=None):
    global _basedir,_beginTime
    _basedir = datapath
    _beginTime = beginTime


def saveData(curTime):
    with open(_getDataFile(),'wb') as f:
        pickle.dump(curTime,f)


def getData():
    if not os.path.exists(_getDataFile()):
        if _beginTime:
            return datetime.strptime(_beginTime,'%y-%m-%d %H:%M:%S')
        else:
            return datetime(year=1970,month=1,day=1)
    else:
        with open(_getDataFile(),'rb') as f:
            return pickle.load(f)
