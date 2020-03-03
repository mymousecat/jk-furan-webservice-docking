#!/usr/bin/env python
# encoding: utf-8
# author: Think
# created: 2018/10/13 11:41

"""
  通过webservice接口，向海口乐康数据上传海南省卫计委 数据
"""

import os
import logging
from suds.client import Client, WebFault
import logconf
from apscheduler.events import EVENT_SCHEDULER_STARTED, \
    EVENT_SCHEDULER_SHUTDOWN, \
    EVENT_JOB_EXECUTED, \
    EVENT_JOB_ERROR, \
    EVENT_JOB_MISSED, \
    EVENT_JOB_ADDED
from apscheduler.schedulers.blocking import BlockingScheduler

from lktj.localdata import initDataPath, saveData, getData
from lktj.localdb import initdb, isInOrders, saveTransLog, TransLog

from lktj.query import getBaseInfo, getBaseInfoByOrderId, getFare, getRecheck, getResults


from utils import xml

from lktj.updataxml import upDataXml

from tj.jktj import getBirthday

log = logging.getLogger(__name__)

SERVICE_URL = 'http://36.101.208.47:8082/checkup/ws/residentServiceWS?wsdl'

# 体检中心编码
CENTER_CODE = '100010'

# 体检中心名称
CENTER_NAME = '系统测试'

# 身高 height
_HEIGHT_TUBE = ()

# 体重 weight
_WEIGHT_TUBE = ()

# 收缩压 systolicBlood

_SYSTOLICBLOOD_TUBE = ()

# 舒张压 diastolicBlood

_DIASTOLICBLOOD_TUBE = ()

# 空腹血糖mmol/L glu

_GLU_TUBE = ()

# 总胆固醇mmol/L totalCholesterol

_TOTALCOLESTEROL_TUBE = ()

# 甘油三酯mmol/L triglycerides

_TRIGLYCERIDES_TUBE = ()

# 低密度脂蛋白mmol/L lowLipoprotein
_LOWLIPOPROTEIN_TUBE = ()

# 高密度脂蛋白mmol/L highLipoprotein

_HIGHLIPOPROTEIN_TUBE = ()

# 左眼裸视视力 leftNaked

_LEFTNAKED_TUBE = ()

# 左眼矫正视力 leftAdjust

_LEFTADJUST_TUBE = ()

# 右眼裸视视力 rightNaked

_RIGHTNAKED_TUBE = ()

# 右眼矫正视力 rightAdjust

_RIGHTADJUST_TUBE = ()

# 生活习惯（工作运动） workHabits

_WORKHABITS_TUBE = ()

# 生活习惯（睡眠） sleepHabits

_SLEEPHABITS_TUBE = ()

# 生活习惯（饮食） eatHabits

_EATHABITS_TUBE = ()

# 生活习惯（其他） otherHabits

_OTHERHABITS_TUBE = ()

# 目前不适症状 nowMalaise

_NOWMALAISE_TUBE = ()

# 目前疾病 nowDisease

_NOWDISEASE_TUBE = ()

# 疾病史  historyDisease

_HISTORYDISEASE_TUBE = ()

# 手术史 historySurgery

_HISTORYSURGERY_TUBE = ()

# 过敏史 historyAllergy
_HISTORYALLERGY_TUBE = ()

# 检查类型
# 一般体格检查 1
_ITEMTYPE_YIBAN_TUBE = (
    '1', '2', '4', '7', '8', '9', '10', '11', '13', '14', '16', '17', '18', '19', '26', '27', '29', '30', '36', '43',
    '44')

# 影像检查 2
_ITEMTYPE_YINGXIANG_TUBE = ('5', '6', '12', '15', '20', '28', '35')

# 实验室检查 3
_ITEMTYPE_SHIYANSHI_TUBE = ('3', '34', '31')

_ERR_CODE = {
    '100': '操作成功',
    '201': '数据解析异常',
    '202': '数据为空',
    '300': '体检数据不符合规范',
    '301': '体检数据基本信息不符合规范',
    '302': '体检数据费用信息不符合规范',
    '303': '体检数据总检信息不符合规范',
    '304': '体检数据体检项目指标信息不符合规范',
    '400': '存储失败',
}


def _saveLocalDB(baseinfo, errCode, msg):
    transLog = TransLog(order_id=baseinfo.order_id, username=baseinfo.username, sex_name=baseinfo.sex_name,
                        age=baseinfo.age, birth=baseinfo.birthday, main_check_date=baseinfo.main_check_date,
                        arrival_date=baseinfo.arrival_date, is_successfull=errCode == '100', trans_msg=msg)

    saveTransLog(transLog)


def _getNameByErrCode(errCode):
    return _ERR_CODE[errCode]


def _getErrCode(returnXml):
    tree = xml.loadFromXml(returnXml)
    return xml.getElementText(tree, '//personInfos/personInfo/dataState')


def _getItemType(department_id):
    departmentId = str(department_id)
    if departmentId in _ITEMTYPE_YIBAN_TUBE:
        return 1
    elif departmentId in _ITEMTYPE_YINGXIANG_TUBE:
        return 2
    elif departmentId in _ITEMTYPE_SHIYANSHI_TUBE:
        return 3
    else:
        return 4


def _getTip(tip):
    if tip is not None:
        if tip.find('高') > -1:
            return '↑'
        elif tip.find('低') > -1:
            return '↓'


def _getRefer(lower, upper):
    if (lower is None and upper is None) or (lower == 0 and upper == 0):
        return
    elif upper == 9999 and lower is not None:
        return '>={}'.format(lower)
    else:
        return '{}~{}'.format(lower, upper)


def _isAbnomal(result):
    if result:
        if result.default_value and result.default_value != result.result_content:
            return True


def _getElementResult(multiValue, isAbnormal, *args, **kwargs):
    if len(args) == 0 or len(kwargs) == 0:
        return

    values = []

    for id in args:
        if isAbnormal:
            if _isAbnomal(kwargs[id]):
                values.append(kwargs[id].result_content)
        else:
            values.append(kwargs[id].result_content)

        if not multiValue:
            break

    if len(values) > 0:
        return ';'.join(values)


def _upDataBy(mcheckdate=None, order_id=None):
    baseinfo = None

    log.info('开始查询数据库获取体检基本信息...')

    if mcheckdate:
        log.info('从数据文件中获取主检时间...')
        mcheckdate = getData()
        log.info('获取的主检时间为:{}'.format(mcheckdate))
        baseinfo = getBaseInfo(mcheckdate)
    elif order_id:
        log.info('获取预约号为:{}的体检基本信息.'.format(order_id))
        baseinfo = getBaseInfoByOrderId(order_id)
    else:
        log.info('主检时间和预约号都为空,无法获取基本信息,程序将近回.')
        return

    if baseinfo is None:
        if mcheckdate:
            log.info('没有查询到比时间:{}更近的体检信息,程序将返回.'.format(mcheckdate))
        elif order_id:
            log.info('没有查询到预约号为:{}体检信息,程序将返回.'.format(order_id))
        return

    log.info('查询到预约号:{} 姓名:{} 年龄:{} 性别:{} 主检时间:{} 的体检信息!'.format(baseinfo.order_id, baseinfo.username, baseinfo.age,
                                                                 baseinfo.sex_name, baseinfo.main_check_date))

    editFlag = '2' if isInOrders(baseinfo.order_id) else '1'

    log.info('开始获取预约号为:{}的收费信息...'.format(baseinfo.order_id))
    fares = getFare(baseinfo.order_id)
    log.info('共获取{}条有效的收费信息.'.format(len(fares)))

    log.info('开始获取预约号为:{}的总检信息...'.format(baseinfo.order_id))
    rechecks = getRecheck(baseinfo.order_id)
    log.info('共获取{}条总检信息.'.format(len(rechecks)))

    log.info('开始获取预约号为:{}的项目结果...'.format(baseinfo.order_id))
    results = getResults(baseinfo.order_id)
    log.info('共获取{}条项目结果'.format(len(results)))

    log.info('开始整理项目结果数据...')
    elementIdList = []
    elementDict = {}
    assemDict = {}

    for result in results:
        assemKey = str(result.element_assem_id)
        elementKey = str(result.element_id)

        # 加入到项目组
        if assemKey not in assemDict.keys():
            assem = {}
            assem['department_id'] = result.department_id
            assem['department_name'] = result.department_name
            assem['element_assem_id'] = result.element_assem_id
            assem['assem_name'] = result.assem_name
            assem['real_name'] = result.real_name
            assem['opt_time'] = result.opt_time
            assem['assem_display_order'] = result.assem_display_order
            assem['merge_words'] = []
            assem['elements'] = []
            assemDict[assemKey] = assem
        assem = assemDict[assemKey]
        assem['merge_words'].append(result.merge_word)

        # 开始处理项目
        if elementKey not in elementIdList:
            elementDict[str(elementKey)] = result
            assem['elements'].append(result)
            elementIdList.append(elementKey)

    elementIdSet = set(elementIdList)

    log.info('开始组装预约号为:{}的xml.'.format(baseinfo.order_id))

    tree = xml.loadFromXml(upDataXml)

    baseInfoPath = '//personInfos/personInfo/baseInfo'

    # 医院编码
    xml.addElement(tree, baseInfoPath, 'orgCode', CENTER_CODE)
    # 医院名称
    xml.addElement(tree, baseInfoPath, 'orgName', CENTER_NAME)

    # 个人预约编号
    xml.addElement(tree, baseInfoPath, 'personalOrder', baseinfo.exam_no)

    # 团体预约编号
    if baseinfo.contract_id:
        xml.addElement(tree, baseInfoPath, 'groupOrder', baseinfo.contract_id)

    # 体检编号
    xml.addElement(tree, baseInfoPath, 'checkNo', baseinfo.order_id)

    # 体检日期
    xml.addElement(tree, baseInfoPath, 'checkDate', baseinfo.arrival_date)

    # 姓名
    xml.addElement(tree, baseInfoPath, 'name', baseinfo.username)

    # 性别代码
    xml.addElement(tree, baseInfoPath, 'sexCode', baseinfo.sex_code)

    # 性别名称
    xml.addElement(tree, baseInfoPath, 'sexName', baseinfo.sex_name)

    # 年龄year
    xml.addElement(tree, baseInfoPath, 'age', baseinfo.age)

    # 出生日期
    xml.addElement(tree, baseInfoPath, 'birthDate', getBirthday(baseinfo.birthday, baseinfo.age))

    # 身份证 idCard
    if baseinfo.cert_id:
        xml.addElement(tree, baseInfoPath, 'idCard', baseinfo.cert_id)

    # 手机 phone
    if baseinfo.telephone:
        xml.addElement(tree, baseInfoPath, 'phone', baseinfo.telephone)

    # 婚姻状况 hyCode hyName
    hyCode = ''
    hyName = ''
    if baseinfo.marital_status:
        if baseinfo.marital_status == '1':
            hyCode = '10'
            hyName = '未婚'
        elif baseinfo.marital_status == '2':
            hyCode = '20'
            hyName = '已婚'
        xml.addElement(tree, baseInfoPath, 'hyCode', hyCode)
        xml.addElement(tree, baseInfoPath, 'hyName', hyName)

    # 工作单位编码 工作单位名称 unitCode unitName
    if baseinfo.org_id:
        xml.addElement(tree, baseInfoPath, 'unitCode', baseinfo.org_id)
        xml.addElement(tree, baseInfoPath, 'unitName', baseinfo.org_name)

    # 身高、体重，血压，高血糖、高血脂指标无可以不填，有则必须填写

    # 身高 height
    height = _getElementResult(False, False, *(set(_HEIGHT_TUBE) & elementIdSet), **elementDict)
    if height:
        xml.addElement(tree, baseInfoPath, 'height', height)

    # 体重 weight
    weight = _getElementResult(False, False, *(set(_WEIGHT_TUBE) & elementIdSet), **elementDict)
    if weight:
        xml.addElement(tree, baseInfoPath, 'weight', weight)

    # 收缩压 systolicBlood

    systolicBlood = _getElementResult(False, False, *(set(_SYSTOLICBLOOD_TUBE) & elementIdSet), **elementDict)
    if systolicBlood:
        xml.addElement(tree, baseInfoPath, 'systolicBlood', systolicBlood)

    # 舒张压 diastolicBlood
    diastolicBlood = _getElementResult(False, False, *(set(_DIASTOLICBLOOD_TUBE) & elementIdSet), **elementDict)
    if diastolicBlood:
        xml.addElement(tree, baseInfoPath, 'diastolicBlood', diastolicBlood)

    # 空腹血糖mmol/L glu
    glu = _getElementResult(False, False, *(set(_GLU_TUBE) & elementIdSet), **elementDict)
    if glu:
        xml.addElement(tree, baseInfoPath, 'glu', glu)

    # 总胆固醇mmol/L totalCholesterol
    totalCholesterol = _getElementResult(False, False, *(set(_TOTALCOLESTEROL_TUBE) & elementIdSet), **elementDict)
    if totalCholesterol:
        xml.addElement(tree, baseInfoPath, 'totalCholesterol', totalCholesterol)

    # 甘油三酯mmol/L triglycerides

    triglycerides = _getElementResult(False, False, *(set(_TRIGLYCERIDES_TUBE) & elementIdSet), **elementDict)
    if triglycerides:
        xml.addElement(tree, baseInfoPath, 'triglycerides', triglycerides)

    # 低密度脂蛋白mmol/L lowLipoprotein
    lowLipoprotein = _getElementResult(False, False, *(set(_LOWLIPOPROTEIN_TUBE) & elementIdSet), **elementDict)
    if lowLipoprotein:
        xml.addElement(tree, baseInfoPath, 'lowLipoprotein', lowLipoprotein)

    # 高密度脂蛋白mmol/L highLipoprotein
    highLipoprotein = _getElementResult(False, False, *(set(_HIGHLIPOPROTEIN_TUBE) & elementIdSet), **elementDict)
    if highLipoprotein:
        xml.addElement(tree, baseInfoPath, 'highLipoprotein', highLipoprotein)

    # 左眼裸视视力 leftNaked
    leftNaked = _getElementResult(False, False, *(set(_LEFTNAKED_TUBE) & elementIdSet), **elementDict)
    if leftNaked:
        xml.addElement(tree, baseInfoPath, 'leftNaked', leftNaked)

    # 左眼矫正视力 leftAdjust
    leftAdjust = _getElementResult(False, False, *(set(_LEFTADJUST_TUBE) & elementIdSet), **elementDict)
    if leftAdjust:
        xml.addElement(tree, baseInfoPath, 'leftAdjust', leftAdjust)

    # 右眼裸视视力 rightNaked
    rightNaked = _getElementResult(False, False, *(set(_RIGHTNAKED_TUBE) & elementIdSet), **elementDict)
    if rightNaked:
        xml.addElement(tree, baseInfoPath, 'rightNaked', rightNaked)

    # 右眼矫正视力 rightAdjust
    rightAdjust = _getElementResult(False, False, *(set(_RIGHTADJUST_TUBE) & elementIdSet), **elementDict)
    if rightAdjust:
        xml.addElement(tree, baseInfoPath, 'rightAdjust', rightAdjust)

    # 生活习惯（工作运动） workHabits
    workHabits = _getElementResult(False, False, *(set(_WORKHABITS_TUBE) & elementIdSet), **elementDict)
    if workHabits:
        xml.addElement(tree, baseInfoPath, 'workHabits', workHabits)

    # 生活习惯（睡眠） sleepHabits
    sleepHabits = _getElementResult(False, False, *(set(_SLEEPHABITS_TUBE) & elementIdSet), **elementDict)
    if sleepHabits:
        xml.addElement(tree, baseInfoPath, 'sleepHabits', sleepHabits)

    # 生活习惯（饮食） eatHabits
    eatHabits = _getElementResult(False, False, *(set(_EATHABITS_TUBE) & elementIdSet), **elementDict)
    if eatHabits:
        xml.addElement(tree, baseInfoPath, 'eatHabits', eatHabits)

    # 生活习惯（其他） otherHabits
    otherHabits = _getElementResult(False, False, *(set(_OTHERHABITS_TUBE) & elementIdSet), **elementDict)
    if otherHabits:
        xml.addElement(tree, baseInfoPath, 'otherHabits', otherHabits)

    # 目前不适症状 nowMalaise
    nowMalaise = _getElementResult(True, True, *(set(_NOWMALAISE_TUBE) & elementIdSet), **elementDict)
    if nowMalaise:
        xml.addElement(tree, baseInfoPath, 'nowMalaise', nowMalaise)

    # 目前疾病 nowDisease
    nowDisease = _getElementResult(True, True, *(set(_NOWDISEASE_TUBE) & elementIdSet), **elementDict)
    if nowDisease:
        xml.addElement(tree, baseInfoPath, 'nowDisease', nowDisease)

    # 疾病史  historyDisease
    historyDisease = _getElementResult(True, True, *(set(_HISTORYDISEASE_TUBE) & elementIdSet), **elementDict)
    if historyDisease:
        xml.addElement(tree, baseInfoPath, 'historyDisease', historyDisease)

    # 手术史 historySurgery
    historySurgery = _getElementResult(True, True, *(set(_HISTORYSURGERY_TUBE) & elementIdSet), **elementDict)
    if historySurgery:
        xml.addElement(tree, baseInfoPath, 'historySurgery', historySurgery)

    # 过敏史 historyAllergy
    historyAllergy = _getElementResult(True, True, *(set(_HISTORYALLERGY_TUBE) & elementIdSet), **elementDict)
    if historyAllergy:
        xml.addElement(tree, baseInfoPath, 'historyAllergy', historyAllergy)

    xml.addElement(tree, baseInfoPath, 'editFlag', editFlag)

    # 费用
    farePath = '//personInfos/personInfo/costInfo'
    log.info('开始计算费用...')
    quotaStandard = 0.00
    quotaCost = 0.00  # 公费
    payCost = 0.00
    totalCost = 0.00
    for fare in fares:
        quotaStandard += 0 if fare.original_amount is None else fare.original_amount
        totalCost += 0 if fare.discount_amount is None else fare.discount_amount
        if fare.unit_or_own == '自费':
            payCost += 0 if fare.original_amount is None else fare.discount_amount
        elif fare.unit_or_own == '公费':
            quotaCost += 0 if fare.discount_amount is None else fare.discount_amount

    xml.addElement(tree, farePath, 'quotaStandard', quotaStandard)
    xml.addElement(tree, farePath, 'quotaCost', quotaCost)
    xml.addElement(tree, farePath, 'payCost', payCost)
    xml.addElement(tree, farePath, 'totalCost', totalCost)

    lastInfosPath = '//personInfos/personInfo/lastInfos'
    log.info('开始总检意见...')
    for recheck in rechecks:
        lastInfo = xml.addElement(tree, lastInfosPath, 'lastInfo')
        xml.addElementByNode(lastInfo, 'lastResult', recheck.merge_word)
        xml.addElementByNode(lastInfo, 'lastAdvice', recheck.recommend)
        xml.addElementByNode(lastInfo, 'lastDoctor', recheck.real_name)
        xml.addElementByNode(lastInfo, 'lastDate', recheck.main_check_date)

    medicalItemsPath = '//personInfos/personInfo/medicalItems'
    log.info('开始项目组...')
    for assemKey in assemDict.keys():
        assem = assemDict[assemKey]
        item = xml.addElement(tree, medicalItemsPath, 'item')
        xml.addElementByNode(item, 'itemCode', assem['element_assem_id'])
        xml.addElementByNode(item, 'itemName', assem['assem_name'])
        xml.addElementByNode(item, 'itemType', _getItemType(assem['department_id']))  # 项目类型需要根据科室计算得出
        xml.addElementByNode(item, 'itemDate', assem['opt_time'])
        xml.addElementByNode(item, 'itemNo', assem['assem_display_order'])
        xml.addElementByNode(item, 'itemResult', ';'.join(set(assem['merge_words'])))
        xml.addElementByNode(item, 'itemDoctor', assem['real_name'])

        # 小项结果
        medicalUnits = xml.addElementByNode(item, 'medicalUnits')
        for result in assem['elements']:
            unit = xml.addElementByNode(medicalUnits, 'unit')
            xml.addElementByNode(unit, 'unitCode', result.element_id)
            xml.addElementByNode(unit, 'unitName', result.element_name)
            xml.addElementByNode(unit, 'unitDate', result.opt_time)
            xml.addElementByNode(unit, 'unitNo', result.element_display_order)
            xml.addElementByNode(unit, 'unitResult', result.result_content)
            xml.addElementByNode(unit, 'unitParam', result.measurement_unit)
            xml.addElementByNode(unit, 'unitRefer',
                                 _getRefer(result.ference_lower_limit, result.ference_upper_limit))
            xml.addElementByNode(unit, 'unitTip', _getTip(result.positive_symbol))

    xmlInfos = xml.tostring(tree, xml_declaration=False, pretty_print=False)

    log.info(xmlInfos)

    log.info('开始上传数据...')
    client = Client(SERVICE_URL)
    r = client.service.sendResidentData(xmlInfos)
    errCode = _getErrCode(r)
    msg = _getNameByErrCode(errCode)

    if errCode == '100':
        log.info('{} - {}'.format(errCode, msg))
    else:
        log.error('{} - {}'.format(errCode, msg))
    # 保存临时数据
    saveData(baseinfo.main_check_date)
    # 写入数据库日志
    _saveLocalDB(baseinfo, errCode, msg)


def upData():
    """
    向卫计委定时传输体检报告
    :return:
    """
    try:
        log.info('从数据文件中获取主检时间...')
        mcheckdate = getData()
        log.info('获取的主检时间为:{}'.format(mcheckdate))
        _upDataBy(mcheckdate=mcheckdate)
    except WebFault as e:
        # 执行Webservice时出错，一般都是对方的错误
        log.error(e)

    except Exception as e:
        log.error(e)


def listener(event):
    if event.code & EVENT_SCHEDULER_STARTED != 0:
        log.info("任务开始...")
    elif event.code & EVENT_SCHEDULER_SHUTDOWN != 0:
        log.info("任务结束...")
    elif event.code & EVENT_JOB_EXECUTED != 0:
        log.info("任务已执行...")
    elif event.code & EVENT_JOB_ERROR != 0:
        log.info("任务执行时出错...")
    elif event.code & EVENT_JOB_ADDED != 0:
        log.info("任务已增加...")
    elif event.code & EVENT_JOB_MISSED != 0:
        log.info("有些任务已错过...")


if __name__ == '__main__':
    # 初始化日志
    logconf.load_my_logging_cfg()
    basedir = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
    log.info('项目数据目录为:{}'.format(basedir))
    log.info('开始初始化本地持久化数据目录...')
    initDataPath(basedir)
    log.info('开始初始化本地数据目录...')
    initdb(basedir)

    scheduler = BlockingScheduler()
    scheduler.add_listener(listener,
                           EVENT_SCHEDULER_STARTED |
                           EVENT_SCHEDULER_SHUTDOWN |
                           EVENT_JOB_EXECUTED |
                           EVENT_JOB_ERROR |
                           EVENT_JOB_MISSED |
                           EVENT_JOB_ADDED
                           )

    # 第天晚上18至第二天凌晨6点上传数据，间隔10秒
    # scheduler.add_job(upData, 'cron', hour='0-6,18-23', second='0,10,20,30,40,50')
    scheduler.add_job(upData, 'cron', hour='*', second='0,10,20,30,40,50')
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        print('任务结束.')
        scheduler.shutdown()
