#!/usr/bin/env python
# encoding: utf-8
# author: Think
# created: 2018/11/28 14:14

"""
  配置文件，用来配置数据库或其它相关信息
"""

import os

_basedir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))

_datadir = os.path.join(_basedir, 'data')

if not os.path.exists(_datadir):
    os.mkdir(_datadir)

datafile = os.path.join(_datadir, 'data.sqlite3')

# 参数配置文件
_confdir = os.path.join(_basedir, 'conf')
if not os.path.exists(_confdir):
    os.mkdir(_confdir)


class Config(object):
    CONF_DATA_FILE = os.path.join(_confdir, 'param.json')

    # jk数据库
    JK_USERNAME_CONST = "lis"
    JK_PASSWORD_CONST = "lisyh"
    # 正式环境
    JK_HOST_CONST = "localhost"
    # 测试环境
    # JK_HOST_CONST = "192.168.75.11"
    JK_DATABASE_CONST = "jk"

    # 默认的本地数据库
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://%s:%s@%s/%s?charset=utf8' % (
        JK_USERNAME_CONST, JK_PASSWORD_CONST, JK_HOST_CONST, JK_DATABASE_CONST)

    # 杭创HIS数据库

    HIS_USERNAME_CONST = "tjuser"
    HIS_PASSWORD_CONST = "1234"
    HIS_HOST_CONST = "172.20.111.240"
    HIS_DATABASE_CONST = "his_fee"

    SQLALCHEMY_BINDS = {
        # 'jk': 'mysql+pymysql://%s:%s@%s/%s?charset=utf8' % (
        #     JK_USERNAME_CONST, JK_PASSWORD_CONST, JK_HOST_CONST, JK_DATABASE_CONST),
        # 'his': 'oracle://%s:%s@%s/%s?charset=gbk' % (
        #     HIS_USERNAME_CONST, HIS_PASSWORD_CONST, HIS_HOST_CONST, HIS_DATABASE_CONST)
        'his': 'mssql+pymssql://%s:%s@%s/%s' % (
            HIS_USERNAME_CONST, HIS_PASSWORD_CONST, HIS_HOST_CONST, HIS_DATABASE_CONST)
    }

    # 数据库迁移目录
    SQLALCHEMY_MIGRATE_REPO = os.path.join(_basedir, 'db_repository')

    SQLALCHEMY_TRACK_MODIFICATIONS = True

    # 体检系统用户名
    JK_EXAM_USERNAME = 'lis'
    # 体检系统密码
    JK_EXAM_PASSWORD = 'lisyh'
    # 体检系统主机的地址
    JK_EXAM_HOST = 'http://localhost'



    from tj.jktj import initHost

    # 初始化体检系统地址
    initHost(JK_EXAM_HOST)

    CSRF_ENABLED = True
    SECRET_KEY = 'AqsS^TjIg4k3CvYdIl4!vG5lYW$WMKG6mW4ui&jrxP1t^6@wcx'


    #失败时，是否发送邮件
    IS_SEND_MAIL = False

    # APScheduler 相关配置

    from apscheduler.jobstores.redis import RedisJobStore

    SCHEDULER_JOBSTORES = {
        'default': RedisJobStore(host='localhost', port=6379)
    }

    SCHEDULER_EXECUTORS = {
        'default': {
            'type': 'threadpool',
            'max_workers': 1
        }
    }

    SCHEDULER_JOB_DEFAULTS = {
        'coalesce': True,
        'max_instances': 1,
        'misfire_grace_time': 600
    }

    JOBS = [
        {
            'id': 'job_main_duty',
            'func': 'yuhelisflask.autotranslis:autoTransLis',
            'args': None,
            'replace_existing': True,
            'trigger': {
                'type': 'interval',
                'seconds': 10
            }
        },
        {
            'id': 'clear_history',
            'func': 'yuhelisflask.db_op:clearHistory',
            'args': None,
            'replace_existing': True,
            'trigger': {
                'type': 'cron',
                'day': '*',
                'hour': '0'
            }

        }
    ]

    SCHEDULER_API_ENABLED = True

    # Boostrap引用的文件在本地
    BOOTSTRAP_SERVE_LOCAL = True

    # 邮件相关信息
    MAIL_MSSSAGE = {
        'host': 'smtp.livingjz.com',
        'username': 'donghai.wu@livingjz.com',
        'password': 'Killme123456',
        'sender': 'donghai.wu@livingjz.com',
        'receivers': ['459834034@qq.com', ],
        'from': '国瑞怡康体检系统'
    }

    LD_ABOUT = {
        'name': '蓝滴体检传输系统',
        'version': '4.2.0',
        'author': '小平',
        'corp': '上海国瑞怡康生物医药科技有限公司'
    }
