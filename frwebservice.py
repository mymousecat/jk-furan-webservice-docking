#!/usr/bin/env python
# encoding: utf-8
# author: Think
# created: 2018/9/20 9:18


"""
  复软 LIS webservice接口 主要实现PACS、LIS与体检
"""

import time

import json

from spyne import Application
from spyne import rpc
from spyne import ServiceBase
from spyne import Unicode, Integer, DateTime
from spyne.protocol.soap import Soap11
from spyne.server.wsgi import WsgiApplication

import logconf
import logging
import re

from furuanhis.xml import validateXML \
    , getReturnXML \
    , tostring \
    , setHeadXML \
    , getElement \
    , getElementText \
    , addElement \
    , addElementByNode \
    , exsistElement \
    , getElementList

from furuanhis.exception import XMLException
from furuanhis.base import getBaseName

from tj.tjexception import TJException
from tj.jktj import login \
    , tjAssert \
    , loadExam \
    , getUserByRealName \
    , loginAssems \
    , getBirthday \
    , getDiseaseByName \
    , saveExamData \
    , saveLisExamData

from tj.tjsaveexam import initSaveExam \
    , addPosReport \
    , addDefaut \
    , addElementResult \
    , addDisease

from tj.query import getLis

log = logging.getLogger(__name__)

IP = "0.0.0.0"
PORT = 8000

JYK = 3


def _getDepartment(risTypeCode):
    # 判断医技类型
    if risTypeCode == '1':  # X 线检查 DR
        return 6
    elif risTypeCode == '4':  # CT
        return 20
    elif risTypeCode == '31':  #胶囊胃镜
        return 46
    else:
        raise XMLException("无效的医技类型编号{0},期望的类型为[{1}]".format(risTypeCode, "1,4,31"))


def _getRisRegData(tree):
    log.info("开始执行{}方法".format("_getRisRegData"))
    # 获取预约号 ORDER_ID
    orderId = getElementText(tree, "//ORDER_ID")
    # 获取医技类型编码
    risTypeCode = getElementText(tree, "//RISTYPE_CODE")
    log.info("获取到预约号为:{0}  医技类型编码为:{1}".format(orderId, risTypeCode))

    # 对应体检科室类型
    department = _getDepartment(risTypeCode)

    # 尝试登录体检系统
    log.info("开始尝试登录体检系统...")

    result = tjAssert(login())

    log.info(result['msg'])

    # 从体检系统中获取本科室的检查信息
    log.info("开始从体检系统中获取体检信息,科室为{},预约号为:{}".format(department, orderId))

    msg = tjAssert(loadExam(department, orderId))

    # 获取体检结果
    exam = msg['msg']

    # 获取体检科室列表
    assems = exam['assems']

    tree = getReturnXML()

    table = addElement(tree, '//ROOT/DETAIL', 'TABLE')

    # 开始操作返回的结果
    for assem in assems:
        record = addElementByNode(table, 'RECORD')
        # 体检号 EXAM_NO
        addElementByNode(record, 'EXAM_NO', exam['examNo'])
        # 预约号 ORDER_ID
        addElementByNode(record, 'ORDER_ID', exam['orderId'])
        # 姓名 USERNAME
        addElementByNode(record, 'USERNAME', exam['username'])
        # 出生日期 BIRTHDAY
        addElementByNode(record, 'BIRTHDAY', getBirthday(exam['birthday'], exam['age']))
        # 性别 SEX_NAME
        addElementByNode(record, 'SEX_NAME', exam['sexVal'])

        # 年龄 AGE
        addElementByNode(record, 'AGE', exam['age'])

        # 手机 TELEPHONE
        addElementByNode(record, 'TELEPHONE', exam['telephone'])

        # 地址 address
        addElementByNode(record, 'ADDRESS', exam['address'])

        # 医技类型编号 RISTYPE_CODE
        addElementByNode(record, 'RISTYPE_CODE', risTypeCode)

        # 医技类型名称 RISTYPE_NAME
        addElementByNode(record, 'RISTYPE_NAME', getBaseName(risTypeCode))

        # 检查部位名称 EXAM_ITEMNAME
        addElementByNode(record, 'EXAM_ITEMNAME', assem['assemName'])

        # 检查部位ID EXAM_ITEMCODE
        addElementByNode(record, 'EXAM_ITEMCODE', assem['assemId'])

        # 申请医生 REQ_DOCTOR
        addElementByNode(record, 'REQ_DOCTOR', '体检中心')

        # 申请日期 REQ_DATE
        addElementByNode(record, 'REQ_DATE', time.strftime('%Y-%m-%d', time.localtime(time.time())))

    setHeadXML(tree, '0000')

    return tostring(tree)


def _confirmRisRegData(tree):
    log.info("开始执行{}方法".format("_confirmRisRegData"))

    # 获取预约号 ORDER_ID
    orderId = getElementText(tree, "//ORDER_ID")

    # 获取确认的部位编码
    itemCode = getElementText(tree, "//EXAM_ITEMCODE")

    # 获取确认医生姓名(如果用户编号，即id和体检中心的一致可否）
    doctorName = getElementText(tree, "//CONFIRM_DOCTOR_NAME")

    log.info("获取到预约号:{} 需要确认的部位id:{}  确认医生姓名:{}".format(orderId, itemCode, doctorName))

    # 尝试登录体检系统
    log.info("开始尝试登录体检系统...")

    result = tjAssert(login())

    log.info(result['msg'])

    # 尝试用得到的真实用户获取用户id
    log.info("尝试用得到的真实用户获取用户id...")

    result = tjAssert(getUserByRealName(doctorName))

    user = result['msg']

    log.info("获取用户id:{}  用户名:{}".format(user['id'], user['name']))

    # 开始登记项目组(使项目组变为登入状态)
    log.info("开始登记项目组")
    result = tjAssert(loginAssems(orderId, itemCode, user['id']))

    log.info(result['msg'])

    return tostring(setHeadXML(getReturnXML(), '0000'))


def _saveRisReport(tree):
    log.info("开始执行{}方法".format("_saveRisReport"))

    orderId = getElementText(tree, '//ORDER_ID')
    log.info("获取预约号:{}".format(orderId))

    risTypeCode = getElementText(tree, '//RISTYPE_CODE')
    log.info("获取医技类型编码:{}".format(risTypeCode))

    # 检查项目，大项ID
    examItemCode = getElementText(tree, '//EXAM_ITEMCODE')
    log.info("获取项目组id:{}".format(examItemCode))

    examItemName = getElementText(tree, '//EXAM_ITEMNAME')
    log.info("获取项目组名字:{}".format(examItemName))

    reportDoctorCode = getElementText(tree, '//CONFIRM_DOCTOR_CODE')
    log.info("获取报告医生编码:{}".format(reportDoctorCode))

    reportDoctorName = getElementText(tree, '//REPORT_DOCTOR_NAME')
    log.info("获取报告医生名字:{}".format(reportDoctorName))

    confirmDoctorCode = getElementText(tree, '//CONFIRM_DOCTOR_CODE')
    log.info("获取审核医生编码:{}".format(confirmDoctorCode))

    confirmDoctorName = getElementText(tree, '//CONFIRM_DOCTOR_NAME')
    log.info("获取审核医生姓名:{}".format(confirmDoctorName))

    findings = getElementText(tree, "//FINDINGS")
    log.info("获取检查所见信息:{}".format(findings))

    impression = getElementText(tree, "//IMPRESSION")
    log.info("获取诊断结果:{}".format(impression))

    sickFlag = getElementText(tree, "//SICK_FLAG")
    log.info("获取疾病标识:{}".format(sickFlag))

    sickName = getElementText(tree, "//SICK_NAME")
    log.info("获取疾病名称:{}".format(sickName))

    # 对应体检科室类型
    department = _getDepartment(risTypeCode)

    # 尝试登录体检系统
    log.info("开始尝试登录体检系统...")

    result = tjAssert(login())

    log.info(result['msg'])

    # 获取报告医生的ID
    result = tjAssert(getUserByRealName(reportDoctorName))
    reporterId = result['msg']['id']
    log.info("获取报告医生ID为:{}".format(reporterId))

    # 获取审核医生ID
    result = tjAssert(getUserByRealName(confirmDoctorName))
    confirmId = result['msg']['id']
    log.info("获取审核者医生ID为:{}".format(confirmId))

    # 从体检系统中获取本科室的检查信息
    log.info("开始从体检系统中获取体检信息,科室为{},预约号为:{},项目组ID:{}".format(department, orderId, examItemCode))

    msg = tjAssert(loadExam(department, orderId, filterAssemIds=examItemCode))

    exam = msg['msg']

    # 初始化保存数据
    saveExam = initSaveExam(exam, department, confirmId, reporterId)

    # 小项结果
    fs = {'others': findings}
    addElementResult(saveExam, exam=exam, opId=reporterId, elementAssemId=examItemCode, **fs)

    # 结论部分，开始拆分影印字段
    log.info('获取结论...')
    # summaries = impression.split('\t') #试着用4个字符串解析换行？
    # summaries = impression.splitlines()
    #
    # summaries =  re.split(r'[\d]+\.',impression)

    imp = '' if impression is None else impression
    if imp.strip() == '':
        raise XMLException('结论不能为空，保存RIS结果失败')

    summaries = re.split(r'\t|\n', imp)

    for s in summaries:
        summary = re.sub(r'^[\d]+\.', '', s.strip())

        # summary = s.strip()

        if len(summary) == 0:
            continue

        log.info('获取结论:{}'.format(summary))

        writeSymbol = None
        diseaseCode = None
        if summary.find('未见异常') >= 0 or summary.find('未见明显异常') >= 0:
            writeSymbol = '03'
        else:
            result = getDiseaseByName(summary)
            if result is None:
                writeSymbol = '02'
            else:
                writeSymbol = '01'
                diseaseCode = result['msg']['id']
        log.info("获取诊断方式:{},疾病名称:{},疾病id:{}".format(writeSymbol, summary, diseaseCode))
        addDisease(saveExam, exam=exam, deptId=department, opId=reporterId, writeSymbol=writeSymbol,
                   diseaseName=summary,
                   diseaseCode=diseaseCode, elementAssemId=examItemCode)

    # 重大阳性
    if sickFlag == '1':
        addPosReport(saveExam, content=findings, advice=sickName, opId=reporterId)

    # 开始提交分科结果
    examData = json.dumps(saveExam)
    log.info(examData)
    log.info('开始提交分科结果...')
    result = tjAssert(saveExamData(examData))
    log.info(result['msg'])

    return tostring(setHeadXML(getReturnXML(), '0000'))


def _getLisRegData(tree):
    log.info("开始执行{}方法".format("_getLisRegData"))
    # 获取条码号
    barcodeId = getElementText(tree, "//BARCODE_ID")
    log.info("获取条码号{}".format(barcodeId))

    # 开始从数据库中获取LIS数据
    log.info("开始从数据库中获取LIS数据...")
    rs = getLis(barcodeId)
    if len(rs) == 0:
        raise Exception("没有查询到条码号为[{}]的LIS数据".format(barcodeId))

    tree = getReturnXML()
    main = getElement(tree, "//MAIN")

    table = None

    isMainSetted = False

    assems = []

    for r in rs:
        # 写入到MAIN中
        if not isMainSetted:
            addElementByNode(main, 'BARCODE_ID', r.barcodeId)
            addElementByNode(main, 'EXAM_NO', r.examNo)
            addElementByNode(main, 'ORDER_ID', r.orderId)
            addElementByNode(main, 'USERNAME', r.username)
            addElementByNode(main, 'BIRTHDAY', getBirthday(r.birthday, r.age))
            addElementByNode(main, 'SEX_NAME', r.sexName)
            addElementByNode(main, 'AGE', r.age)
            addElementByNode(main, 'TELEPHONE', r.telephone)
            addElementByNode(main, 'ADDRESS', r.address)
            addElementByNode(main, 'SPECIMEN_TYPE_NAME', r.specimenTypeName)
            addElementByNode(main, 'LIS_ELEMENT_ASSEM_ID', r.specimenRemark)
            addElementByNode(main, 'REQ_DOCTOR', r.reqDoctor)
            addElementByNode(main, 'REQ_DATE', r.arrivalTime)
            isMainSetted = True

        if not exsistElement(tree, '//ROOT/DETAIL/TABLE'):
            # 写入到DETAIL中，大项+小项
            table = addElement(tree, '//ROOT/DETAIL', 'TABLE')

        key = '{}|{}|{}'.format(r.orderId, r.elementAssemId, r.elementId)
        record = addElementByNode(table, 'RECORD')
        # 写入小项
        addElementByNode(record, 'LIS_ELEMENT_ID', r.lisElementId)
        addElementByNode(record, 'ELEMENT_NAME', r.elementName)
        addElementByNode(record, 'FK_KEY', key)

        # 写入项目组名字列表
        assems.append(r.elementAssemName)

    # 写入项目组名称的拼接，组成大类的名称

    singleAssems = list(set(assems))

    singleAssems.sort(key=assems.index)

    sAssems = ','.join(singleAssems)

    addElementByNode(main, 'ELEMENT_ASSEM_NAME', sAssems)

    setHeadXML(tree, '0000')

    return tostring(tree)


def _confirmLisRegData(tree):
    log.info("开始执行{}方法".format("_confirmLisRegData"))
    return tostring(setHeadXML(getReturnXML(), '0000'))


def _saveLisReport(tree):
    log.info("开始执行{}方法".format("_saveLisReport"))

    barcodeId = getElementText(tree, "//BARCODE_ID")
    log.info("获取条码号:{}".format(barcodeId))

    orderId = getElementText(tree, '//ORDER_ID')
    log.info("获取预约号:{}".format(orderId))

    operatorCode = getElementText(tree, "//OPERATOR_ID")
    log.info("获取检验者ID:{}".format(operatorCode))

    operatorName = getElementText(tree, "//OPERATOR_NAME")
    log.info("获取检验者姓名:{}".format(operatorName))

    auditCode = getElementText(tree, "//AUDIT_ID")
    log.info("获取审核者ID:{}".format(auditCode))

    auditName = getElementText(tree, "//AUDIT_NAME")
    log.info("获取审核者姓名:{}".format(auditName))

    # 获取项目结果
    log.info("开始获取项目结果...")

    records = getElementList(tree, "//ROOT/DETAIL/TABLE/RECORD")

    acceptAssems = {}

    acceptElements = {}

    for record in records:

        lisElementId = getElementText(record, "LIS_ELEMENT_ID")
        lisElementName = getElementText(record, "LIS_ELEMENT_NAME")
        result = getElementText(record, "CONTENT_RESULT")
        unit = getElementText(record, "RESULT_UNIT")
        # fe getElementText(record,"//FERENCE_VALUE")
        lower = getElementText(record, "FERENCE_LOWER_LIMIT")
        upper = getElementText(record, "FERENCE_UPPER_LIMIT")
        positiveSymbol = getElementText(record, "POSITIVE_SYMBOL")
        criticalSymbol = getElementText(record, "CRITICAL_VALUES_SYMBOL")
        fkKey = getElementText(record, "FK_KEY")

        log.info('fkey:{}'.format(fkKey))

        if fkKey is None:
            raise XMLException('项目:{}  {}的fkKey值为空.'.format(lisElementId, lisElementName))

        # 解析项目组ID和小项ID
        keys = fkKey.split('|')
        if len(keys) != 3:
            raise TJException("无效的FK_KEY:{} 条码号:{} 预约号:{}  项目:{}".format(fkKey, barcodeId, orderId, lisElementName))

        assemId = keys[1]
        elementId = keys[2]

        if assemId not in acceptAssems.keys():
            acceptAssems[assemId] = []

        item = {}

        item['lisElementId'] = lisElementId
        item['lisElementName'] = lisElementName
        item['result'] = result
        item['unit'] = unit
        item['lower'] = lower
        item['upper'] = upper
        item['positiveSymbol'] = positiveSymbol
        item['criticalSymbol'] = criticalSymbol
        item['elementId'] = elementId

        acceptAssems[assemId].append(item)

        acceptElements[elementId] = item

    # 尝试登录体检系统
    log.info("开始尝试登录体检系统...")

    result = tjAssert(login())

    log.info(result['msg'])

    # 获取检验医生的ID
    result = tjAssert(getUserByRealName(operatorName))
    operatorId = result['msg']['id']
    log.info("获取检验医生的ID为:{}".format(operatorId))

    # 获取审核医生ID
    result = tjAssert(getUserByRealName(auditName))
    auditId = result['msg']['id']
    log.info("获取审核者医生ID为:{}".format(auditId))

    # 获取体检项目
    # 从体检系统中获取本科室的检查信息

    for key in acceptAssems.keys():
        log.info("开始从体检系统中获取体检信息,科室为{},预约号为:{},项目组ID:{}".format(JYK, orderId, key))
        msg = tjAssert(loadExam(JYK, orderId, filterAssemIds=key))
        exam = msg['msg']

        lisDatas = {

            'orderId': orderId,
            'elementAssemId': key,
            'departmentId': JYK,
            'sampleOpId': operatorId,
            'opId': auditId,
            'items': []
        }

        assem = exam['assems'][0]

        elements = assem['elements']

        log.info(acceptElements)

        for e in elements:
            ekey = str(e['elementId'])
            if ekey not in acceptElements.keys():
                # 这里报异常，先去掉，无法报存
                raise TJException(
                    "管号为:{}  预约号:{}  项目组:{} 项目:{}在审核的结果中不存在，不能保存到检验结果".format(barcodeId, orderId, assem['assemName'],
                                                                              e['elementName']))
                # continue

            acceptElement = acceptElements[ekey]

            lisElement = {}




            lisElement['elementId'] = e['elementId']
            lisElement['checkElementResult'] = acceptElement['result']
            lisElement['ferenceLower'] = acceptElement['lower']
            lisElement['ferenceUpper'] = acceptElement['upper']
            lisElement['unit'] = acceptElement['unit']
            lisElement['resultType'] = e['resultType']
            lisElement['referenceType'] = '1'  # e['refType']

            # 危机值的标识？
            lisElement['criticalValuesSymbol'] = acceptElement['criticalSymbol']

            # 阳性标识，如何表达呢？
            if acceptElement['positiveSymbol'] == '↑':
                lisElement['positiveSymbol'] = '高'
            elif acceptElement['positiveSymbol'] == '↓':
                lisElement['positiveSymbol'] = '低'
            else:
                lisElement['positiveSymbol'] = None

            lisDatas['items'].append(lisElement)

        # 开始保存LIS结果
        examData = json.dumps(lisDatas)
        log.info(examData)

        log.info("开始保存LIS结果....")
        result = tjAssert(saveLisExamData(examData))
        log.info(result['msg'])

    return tostring(setHeadXML(getReturnXML(), '0000'))


class FuruanService(ServiceBase):
    """
      实现复软科技的Webservice接口
    """

    @rpc(Unicode, _returns=Unicode)
    def sendMessage(self, xmldoc):
        """
          通用的复软Webservice接口
        """
        # 开始检测传入的xmldoc

        log.info("收到参数:{}".format(xmldoc))

        tree = None
        try:
            tree = validateXML(xmldoc)
            # 开始获取ACTION
            e = getElement(tree, '/ROOT/HEAD/ACTION')
            action = e.text
            log.info("获取到ACTION为{0}".format(action))
            if action == "getRisRegData":
                return _getRisRegData(tree)
            elif action == "confirmRisRegData":
                return _confirmRisRegData(tree)
            elif action == "saveRisReport":
                return _saveRisReport(tree)
            elif action == "getLisRegData":
                return _getLisRegData(tree)
            elif action == "confirmLisRegData":
                return _confirmLisRegData()
            elif action == "saveLisReport":
                return _saveLisReport(tree)
            else:
                raise XMLException("无效的ACTION{}".format(action))

        except XMLException as e:
            # 输入的XML解析错误
            log.error(e)
            return tostring(setHeadXML(getReturnXML(), 'E0001', repr(e)))
        except TJException as e:
            # 体检系统错误
            log.error(e)
            return tostring(setHeadXML(getReturnXML(), 'E0003', repr(e)))
        except Exception as e:
            # 其它错误 E0002为数据库错误
            log.error(e)
            return tostring(setHeadXML(getReturnXML(), 'E0003', repr(e)))


soap_app = Application(services=[FuruanService],
                       tns='ws.greenikon.com',
                       in_protocol=Soap11(validator='lxml'),
                       out_protocol=Soap11(pretty_print=True))

wsgi_app = WsgiApplication(soap_app)

if __name__ == "__main__":

    logconf.load_my_logging_cfg()

    from wsgiref.simple_server import make_server

    log.info("listening to http://%s:%d" % (IP, PORT))
    log.info("wsdl is at: http://%s:%d/?wsdl" % (IP, PORT))
    server = make_server(IP, PORT, wsgi_app)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        log.info('shutting down the web server')
        server.socket.close()
