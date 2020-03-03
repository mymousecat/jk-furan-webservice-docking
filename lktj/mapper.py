#!/usr/bin/env python
# encoding: utf-8
# author: Think
# created: 2018/9/20 15:02

"""
数据表OR映射
"""

from sqlalchemy import String, DateTime, Column, Float, Integer
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class BaseInfo(Base):
    """
      基础数据
    """
    __tablename__ = 'v_lk_baseinfo'
    order_id = Column(String, primary_key=True)
    contract_id = Column(String)
    exam_no = Column(String)
    arrival_date = Column(DateTime)
    username = Column(String)
    sex_code = Column(String)
    sex_name = Column(String)
    birthday = Column(DateTime)
    age = Column(Integer)
    cert_id = Column(String)
    telephone = Column(String)
    marital_status = Column(String)
    marital_name = Column(String)
    email = Column(String)
    org_id = Column(String)
    org_name = Column(String)
    main_check_date = Column(DateTime)
    exam_status = Column(String)


class Fare(Base):
    # """
    #   费用
    # """
    __tablename__ = 'v_lk_fare'
    id = Column(String, primary_key=True)
    order_id = Column(String)
    original_amount = Column(Float)
    discount_amount = Column(Float)
    unit_or_own = Column(String)


class Recheck(Base):
    """
      总检建议
    """
    __tablename__ = 'v_lk_recheck'
    id = Column(String, primary_key=True)
    order_id = Column(String)
    recommend = Column(String)
    merge_word = Column(String)
    main_check_date = Column(DateTime)
    real_name = Column(String)


class Results(Base):
    """
      检查结果列表
    """
    __tablename__ = 'v_lk_results'
    id = Column(String, primary_key=True)
    order_id = Column(String)
    department_id = Column(String)
    department_name = Column(String)
    element_assem_id = Column(String)
    assem_name = Column(String)
    real_name = Column(String)
    merge_word = Column(String)
    assem_display_order = Column(String)
    element_id = Column(String)
    element_name = Column(String)
    element_display_order = Column(String)
    opt_time = Column(DateTime)
    default_value = Column(String)
    result_content = Column(String)
    measurement_unit = Column(String)
    ference_lower_limit = Column(Float)
    ference_upper_limit = Column(Float)
    positive_symbol = Column(String)

