#!/usr/bin/env python
# encoding: utf-8
# author: Think
# created: 2018/9/27 15:47

"""
  异常结果
"""

class XMLException(Exception):
    """
      XML输入异常
    """
    def __init__(self,msg):
        self.msg = msg

    def __repr__(self):
        return "[{0}]{1}".format(self.__class__.__name__,self.msg)

