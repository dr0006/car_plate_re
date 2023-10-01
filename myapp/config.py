# -*- coding: utf-8 -*-
"""
@File  : config.py
@author: FxDr
@Time  : 2023/09/30 15:39
@Description:flask的配置信息文件
"""

import os


class Config:
    # 通用配置
    DEBUG = True  # debug 开启 在生产中不要开debug
    SECRET_KEY = os.environ.get('SECRET_KEY', '5201314')
    # MySQL 数据库配置
    MYSQL_CONFIG = {
        'user': 'root',  # MySQL 用户名
        'password': 'root',  # MySQL 密码
        'host': 'localhost',  # MySQL 主机地址
        'port': 3306,  # MySQL 端口号，默认为 3306
        'db': 'car_plate_re'  # 数据库名称
    }


# 使用字典映射配置名称到配置类
config_by_name = {
    'default': Config,
}
