#!/usr/bin/env python
# encoding: utf-8
# author: Think
# created: 2018/9/27 15:30

"""
  复软科技的xml接口
"""


from lxml import etree
from  furuanhis.exception import XMLException
import time

"""
  通用返回接口
"""
_RESP_XML = "<ROOT>"\
              "<HEAD>"\
                "<RETURNCODE/>"\
                "<RETURNMESSAGE/>"\
                "<RETURNTIME/>"\
                "</HEAD>"\
               "<MAIN/>"\
               "<DETAIL/>"\
             "</ROOT>"





def validateXML(xmldoc):
    """
    判断xmldoc的有效性,如果有效，则返回解析后的实例
    :param xmldoc:
    :return:
    """
    try:
        if xmldoc:
            tree = etree.fromstring(xmldoc.encode(encoding="utf-8"))
            path = '/ROOT/HEAD/ACTION'
            e = _getElement(tree,path)
            if e is None:
                raise XMLException('路径{0}不存在，无效的输入XML,{1}'.format(path,xmldoc))
            return tree
    except Exception as e:
        raise XMLException(repr(e))


def getReturnXML():
    """
    返回通用的XML,如果失败，则返回None
    :param xmldoc:
    :return:
    """
    try:
        return etree.fromstring(_RESP_XML)
    except :
        return None



def _getElementList(tree,nodeName):
    if tree is not None:
        return  tree.xpath(nodeName)


def _getElement(tree,nodeName):
    if tree is not None:
       nodes = tree.xpath(nodeName)
       if len(nodes) > 0:
          return nodes[0]


def _setElement(node,text):
    if node is not None:
        node.text = text


def exsistElement(tree,nodename):
    e = _getElement(tree,nodename)
    return e is not None


def getElement(tree,nodeName):
    e = _getElement(tree,nodeName)
    if e is None:
        raise XMLException('路径{0}不存在，无效的输入XML'.format(nodeName))
    else:
        return e

def getElementList(tree,nodeName):
    nodes = _getElementList(tree,nodeName)
    if len(nodes) == 0:
        raise XMLException("路径{}不存在，无效的输入XML".format(nodeName))
    else:
        return nodes



def getElementText(tree,nodeName):
    e = getElement(tree,nodeName)
    return e.text


def addElement(tree,path,newNodeName,text=None):
    if tree is not None:
        e = getElement(tree,path)
        child = etree.SubElement(e,newNodeName)
        if text is not None:
            child.text = str(text)
        return child


def addElementByNode(node,newNodeName,text=None):
    if node is not None:
        child = etree.SubElement(node, newNodeName)
        if text:
            child.text = str(text)
        return child



def setHeadXML(tree,code,msg=None):
    """
    设置xml的头部状态码,并返回tree
    :param tree:
    :param code:
    :param msg:
    :return:
    """
    _setElement(_getElement(tree,'//RETURNCODE'),code)
    if msg:
       _setElement(_getElement(tree, '//RETURNMESSAGE'), msg)

    _setElement(_getElement(tree, '//RETURNTIME'), time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())))
    return tree


def tostring(tree):
    return str(etree.tostring(tree,encoding="utf-8",xml_declaration=True,pretty_print=True),encoding="utf-8")


if __name__ == '__main__':
    s = "a"
    print(s == "a")




