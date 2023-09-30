# -*- coding: utf-8 -*-
"""
@File  : sql_car.py
@author: FxDr
@Time  : 2023/09/30 16:23
@Description:
"""
import pymysql  # 用于mysql的操作
from config import config_by_name


def sql_connection():
    """
    连接数据库返回操作游标对象
    :return:
    """
    config_name = 'default'
    db_config = config_by_name[config_name]
    # db = pymysql.connect(host="localhost", user="root", password="root", db="car_plate_re")
    db = pymysql.connect(**db_config.MYSQL_CONFIG)
    #  用cursor() 方法获取操作游标
    cursor = db.cursor()
    return cursor, db


# 创建用户
def create_user(username, email, password):
    cursor, db = sql_connection()
    # 插入新用户记录
    cursor.execute("INSERT INTO users (username, email, password) VALUES (%s, %s, %s)", (username, email, password))
    db.commit()
    cursor.close()
    db.cursor()
    return "注册成功"


# 登录
def sql_login(email, password):
    cursor, db = sql_connection()
    cursor.execute("SELECT * FROM users WHERE email=%s AND password=%s", (email, password))
    user = cursor.fetchone()
    cursor.close()
    db.close()
    return user
