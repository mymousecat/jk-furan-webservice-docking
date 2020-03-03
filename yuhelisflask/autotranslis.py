#!/usr/bin/env python
# encoding: utf-8
# author: Think
# created: 2018/11/20 9:14
"""
  自动传输LIS数据到体检系统中
"""

import logging

from . import app
from yuhelisflask.paramconfig import getValue, setValue
from yuhelisflask.db_op import getNextBarcode, getItems, saveTransLog, getAssems, getAssemsDetail, need_push_mail
from yuhelisflask.models import TransLog
from yuhelisflask.translisbyassem import transLis
from datetime import datetime
from tj.tjexception import TJException
from yuhelisflask.job import publishMail

log = logging.getLogger(__name__)


def _get_next_id(cur_id, lis_result_ids):
    ids = [x for x in lis_result_ids if x > cur_id]
    ids.sort()
    l0 = len(ids) - 1
    if l0 == 0:
        return ids[0]
    while l0 > 0:
        if ids[l0] - ids[0] == l0:
            return ids[l0]
        l0 = l0 - 1
    return ids[0]


def _saveTransLog(examAssem, sample_date, operator_id, operator_name, is_successful, msg):
    translog = TransLog()
    translog.order_id = examAssem.ORDER_ID
    translog.barcode_id = examAssem.BARCODE_ID

    translog.element_assem_id = examAssem.ELEMENT_ID
    translog.element_assem_name = examAssem.ELEMENT_NAME

    translog.username = examAssem.USERNAME
    translog.sex_name = examAssem.SEX_NAME
    translog.age = examAssem.AGE

    translog.operator_id = operator_id if operator_id is not None else 0

    translog.operator_name = operator_name if operator_name is not None else '系统自动'

    translog.sample_date = sample_date if sample_date is not None else datetime.now()
    translog.is_successfull = is_successful
    translog.trans_msg = msg

    translog.trans_time = datetime.now()
    translog.trans_date = datetime.now()

    # if not translog.is_successfull:

    saveTransLog(translog)

    # 是否发送发送邮件
    if app.config['IS_SEND_MAIL'] and need_push_mail(translog.barcode_id, translog.element_assem_id):
        publishMail(translog)


def autoTransLis():
    """
    自动传输HIS数据到体检系统中
    """
    try:
        log.info('开始从配置文件获取ID和条码号...')
        config = getValue()
        log.info('从配置文件获取到ID:{} 条码号为:{}'.format(config['id'], config['barcodeId']))
        cur_id = 0 if config['id'] is None else config['id']
        log.info('开始从HIS系统中获取LIS结果数据...')
        barcodeId = getNextBarcode(config['id'], config['barcodeId'])
        log.info('获取到的barcode值为:{}'.format(barcodeId))
        if barcodeId is None:
            log.info('没有获取到最新的barcode值，程序将返回...')
            return

        log.info('从HIS系统中获取LIS项目结果,条码号为{}'.format(barcodeId))
        lisResultItems = getItems(barcodeId)
        log.info('从HIS获取了{}条项目结果'.format(len(lisResultItems)))
        if len(lisResultItems) == 0:
            log.info('没有从HIS系统中获取到项目结果,条码号为{},程序将返回...'.format(barcodeId))
            return

        lis_result_ids = []
        lis_result_dict = {}

        for lisResult in lisResultItems:
            lis_result_ids.append(lisResult.ID)
            if lisResult.LIS_ELEMENT_ID is not None:
                key = str(lisResult.LIS_ELEMENT_ID)
                lis_result_dict[key] = lisResult

        nextId = _get_next_id(cur_id, lis_result_ids)

        sample_date = lisResultItems[0].SAMPLE_DATE

        log.info('开始从体检系统中获取项目组信息，条码号为:{}'.format(barcodeId))

        assems = getAssems(barcodeId)
        if len(assems) == 0:
            log.error('没有从体检系统中获取条码号为{}的项目组信息，下一个ID为{}，程序将退出...'.format(barcodeId, nextId))
            setValue(nextId, barcodeId)
            return

        log.info('开始分析体检项目数据...')

        for assem in assems:
            try:
                str_item_results = transLis(assem.DEPARTMENT_ID, assem.ORDER_ID, assem.ELEMENT_ID, lis_result_dict)
                # 如果保存成功
                msg = '条码号:{} 预约号:{} 项目组ID:{} 项目组名:{}保存LIS数据成功'.format(assem.BARCODE_ID,
                                                                       assem.ORDER_ID,
                                                                       assem.ELEMENT_ID,
                                                                       assem.ELEMENT_NAME)
                log.info(msg)
                _saveTransLog(assem, sample_date, None, None, True,
                              '保存LIS数据成功!' + '\n' + str_item_results)
            except TJException as e:
                msg = '条码号:{} 预约号:{} 项目组ID:{} 项目组名:{}保存LIS数据失败!【{}】'.format(assem.BARCODE_ID,
                                                                            assem.ORDER_ID,
                                                                            assem.ELEMENT_ID,
                                                                            assem.ELEMENT_NAME, repr(e))
                log.error(msg)
                _saveTransLog(assem, sample_date, None, None, False,
                              repr(e))

        msg = '条码号:{} 预约号:{}  nextId:{}  barcodeId:{}   保存LIS完成'.format(assem.BARCODE_ID,
                                                                        assem.ORDER_ID,
                                                                        nextId,
                                                                        barcodeId
                                                                        )

        log.info(msg)
        setValue(nextId, barcodeId)

    except Exception as e:
        log.exception(e)
