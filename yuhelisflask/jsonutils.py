# -*- coding: utf-8 -*-

"""
-------------------------------------------------
   File Name：     jsonencoder
   Description :
   Author :       wdh
   date：          2019/1/11
-------------------------------------------------
   Change Activity:
                   2019/1/11:
-------------------------------------------------
"""

import json
import datetime
from sqlalchemy.orm.state import InstanceState
from utils.class2dict import class2Dict

class CJsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, datetime.date):
            return obj.strftime("%Y-%m-%d")
        elif isinstance(obj, InstanceState):
            return None
        else:
            return json.JSONEncoder.default(self, obj)


def toJson(aDict):
    return json.dumps(aDict,ensure_ascii=False,cls=CJsonEncoder)