#!/usr/bin/env python
# encoding: utf-8
# author: Think
# created: 2018/11/28 14:05
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from yuhelisflask.config import Config
from flask_apscheduler import APScheduler
from flask_bootstrap import Bootstrap


app = Flask(__name__)

app.config.from_object(Config())


db = SQLAlchemy(app)

Bootstrap(app=app)

scheduler = APScheduler()
scheduler.init_app(app=app)

from yuhelisflask import views

