# -*- coding: utf-8 -*-
"""
@File  : run.py
@author: FxDr
@Time  : 2023/09/30 16:08
@Description:
"""
from myapp.app import create_app

if __name__ == '__main__':
    config_name = 'default'  # 默认配置
    # 创建应用对象
    app = create_app(config_name)
    # 运行
    app.run()
