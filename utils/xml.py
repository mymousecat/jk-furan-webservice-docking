#!/usr/bin/env python
# encoding: utf-8
# author: Think
# created: 2018/10/13 14:48
"""
  xml操作
"""

from lxml import etree
from utils.xmlexception import XMLException

def loadFromXml(xmlString):
    return etree.fromstring(xmlString.encode("utf-8"))


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
        if text is not None:
            child.text = str(text)
        return child

def tostring(tree,xml_declaration=True,pretty_print=True):
    return str(etree.tostring(tree,encoding="utf-8",xml_declaration=xml_declaration,pretty_print=pretty_print),encoding="utf-8")

