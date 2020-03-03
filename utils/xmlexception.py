#!/usr/bin/env python
# encoding: utf-8
# author: Think
# created: 2018/10/13 15:04

class XMLException(Exception):
    """
      XML输入异常
    """
    def __init__(self,msg):
        self.msg = msg

    def __repr__(self):
        return "[{0}]{1}".format(self.__class__.__name__,self.msg)