#!/usr/bin/env python
# encoding: utf-8
# author: Think
# created: 2018/11/28 15:19

from migrate.versioning import api
from yuhelisflask.config import SQLALCHEMY_DATABASE_URI,SQLALCHEMY_MIGRATE_REPO
from yuhelisflask import db
import os

db.create_all(bind=None)

if not os.path.exists(SQLALCHEMY_MIGRATE_REPO):
   api.create(SQLALCHEMY_MIGRATE_REPO,'database repository')
   api.version_control(SQLALCHEMY_DATABASE_URI,SQLALCHEMY_MIGRATE_REPO)
else:
    api.version_control(SQLALCHEMY_DATABASE_URI,SQLALCHEMY_MIGRATE_REPO,api.version(SQLALCHEMY_MIGRATE_REPO))
