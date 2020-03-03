#!/usr/bin/env python
# encoding: utf-8
# author: Think
# created: 2018/9/20 15:02

"""
数据表OR映射
"""

from sqlalchemy import String, DateTime, MetaData, Table, Column
from sqlalchemy.orm import mapper

metadata = MetaData()

lis = Table("v_lis",
            metadata,
            Column('uuid', String, primary_key=True),
            Column('barcodeId', String),
            Column('examNo', String),
            Column('orderId', String),
            Column('username', String),
            Column('birthday', DateTime),
            Column('sexName', String),
            Column('age', String),
            Column('telephone', String),
            Column('address', String),
            Column('specimenTypeName', String),
            Column('specimenColor', String),
            Column('specimenRemark', String),
            Column('lisElementAssemId', String),
            Column('elementAssemId', String),
            Column('elementAssemName', String),
            Column('lisElementId', String),
            Column('elementId', String),
            Column('elementName', String),
            Column('reqDoctor', String),
            Column('arrivalTime', DateTime)
            )


class Lis(object):
    def __init__(self, uuid,
                 barcodeId, examNo, orderId,
                 username, birthday, sexName, age,
                 telephone, address, specimenTypeName, specimenColor, specimenRemark,
                 lisElementAssemId, elementAssemId, elementAssemName,
                 lisElementId, elementId, elementName, reqDoctor, arrivalTime):
        self.uuid = uuid
        self.barcodeId = barcodeId
        self.examNo = examNo
        self.orderId = orderId
        self.username = username
        self.birthday = birthday
        self.sexName = sexName
        self.age = age
        self.telephone = telephone
        self.address = address
        self.specimenTypeName = specimenTypeName
        self.specimenColor = specimenColor
        self.specimenRemark = specimenRemark
        self.lisElementAssemId = lisElementAssemId
        self.elementAssemId = elementAssemId
        self.elementAssemName = elementAssemName
        self.lisElementId = lisElementId
        self.elementId = elementId
        self.elementName = elementName
        self.reqDoctor = reqDoctor
        self.arrivalTime = arrivalTime


mapper(Lis, lis)
