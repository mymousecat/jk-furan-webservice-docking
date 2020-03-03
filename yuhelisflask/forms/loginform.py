#!/usr/bin/env python
# encoding: utf-8
# author: Think
# created: 2018/11/29 10:11

from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,SubmitField
from wtforms.validators import data_required

class LoginForm(FlaskForm):
    username = StringField('请输入用户名',validators=[data_required('用户名不能为空')])
    password = PasswordField('请输入密码',validators=[data_required('密码不能为空')])
