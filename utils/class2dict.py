# -*- coding: utf-8 -*-

"""
-------------------------------------------------
   File Name：     class2dict
   Description :
   Author :       wdh
   date：          2019/1/11
-------------------------------------------------
   Change Activity:
                   2019/1/11:
-------------------------------------------------
"""

def class2Dict(obj):
    '''把对象(支持单个对象、list、set)转换成字典'''
    is_list = obj.__class__ == [].__class__
    is_set = obj.__class__ == set().__class__

    if is_list or is_set:
        obj_arr = []
        for o in obj:
            # 把Object对象转换成Dict对象
            dict = {}
            dict.update(o.__dict__)
            obj_arr.append(dict)
        return obj_arr
    else:
        dict = {}
        dict.update(obj.__dict__)
        return dict
