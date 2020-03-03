#!/usr/bin/env python
# encoding: utf-8
# author: Think
# created: 2018/11/29 9:53


from flask import render_template,request
from yuhelisflask import app
from yuhelisflask .resp import Resp
from yuhelisflask.jsonutils import toJson
from yuhelisflask import db_op
from utils.class2dict import class2Dict



@app.route('/about')
def about():
    resp = None
    try:
        resp = Resp(0, '操作成功！',app.config['LD_ABOUT'])
    except Exception as e:
        resp = Resp(1, '获取关于信息失败！[{}]'.format(str(e)), None)
    return toJson(class2Dict(resp))


@app.route('/query')
def query():
    limit = request.args.get('limit',25,int)
    offset = request.args.get('offset',0,int)
    barcodeId = request.args.get('barcodeId',None)
    orderId = request.args.get('orderId',None)
    onlyErr = request.args.get('onlyErr','false')
    beginDate = request.args.get('beginDate',None)
    endDate = request.args.get('endDate',None)
    page = db_op.query(limit,offset,barcodeId,orderId,onlyErr,beginDate,endDate)
    r = {}
    r['total'] = page.total
    r['rows'] = class2Dict(page.items)
    return toJson(r)


@app.route('/')
def index():
    return render_template('index.html', title='蓝滴体检对接')