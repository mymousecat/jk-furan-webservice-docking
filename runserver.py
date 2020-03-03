#!/usr/bin/env python
# encoding: utf-8
# author: Think
# created: 2018/11/28 14:07

import logging
from yuhelisflask import app,scheduler
from logconf import load_my_logging_cfg


log = logging.getLogger(__name__)

if __name__ == '__main__':
    #初始化日志
    load_my_logging_cfg()

    scheduler.start()

    app.run(host='0.0.0.0',port=8081,debug=False)