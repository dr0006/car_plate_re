# -*- coding: utf-8 -*-
"""
@File  : sql_car.py
@author: FxDr
@Time  : 2023/09/30 16:23
@Description:
"""
import os

import pymysql  # 用于mysql的操作
from config import config_by_name


# 数据库连接
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
    # 先查询是否以及注册
    cursor.execute("SELECT * FROM users WHERE email=%s", email)
    user = cursor.fetchone()
    # print(user)
    if user is None:
        # 插入新用户记录
        cursor.execute("INSERT INTO users (username, email, password) VALUES (%s, %s, %s)", (username, email, password))
        db.commit()
        cursor.close()
        db.cursor()
        return True  # "注册成功"
    else:
        return False  # "该用户已存在"


# 登录
def sql_login(email, password):
    cursor, db = sql_connection()
    cursor.execute("SELECT * FROM users WHERE email=%s AND password=%s", (email, password))
    user = cursor.fetchone()
    cursor.close()
    db.close()
    return user


# 进行识别记录的上传
def sql_reload(email, code, confidence):
    target_directory = "./static/re_image/{}".format(email)
    # 如果目标目录不存在，则创建它
    if not os.path.exists(target_directory):
        os.makedirs(target_directory)

    target_path = target_directory + "/{}.jpg".format(code)
    # print(target_path)

    # 读取本地图片文件为二进制数据
    with open('./static/images/recognized_image.png', 'rb') as file:
        image_data = file.read()

    # 打开目标保存文件
    with open(target_path, 'wb') as target_file:
        # 将图片内容写入目标文件
        target_file.write(image_data)

    cursor, db = sql_connection()
    target_path = target_path[1:]
    # print(target_path)
    try:
        # 插入数据到数据库表中
        cursor.execute(
            "INSERT INTO car_plate (user_email, image_url, recognition_result, confidence) VALUES (%s, %s, %s, %s)",
            (email, target_path, code, confidence))
        # 提交
        db.commit()
        return True  # 成功就返回真
    except Exception as e:
        # 如果发生错误，回滚更改
        db.rollback()
        print("发生错误:", str(e))
        return False  # 不成功就返回False
    finally:
        # 关闭游标和数据库连接
        cursor.close()
        db.close()
