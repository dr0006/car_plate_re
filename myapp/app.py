# -*- coding: utf-8 -*-
"""
@File  : app.py
@author: FxDr
@Time  : 2023/09/30 15:38
@Description:
"""
import os

from flask import Flask, render_template, request, flash, redirect

from config import config_by_name
from sql_car import create_user, sql_login, sql_connection

# 导入cv相关库
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import hyperlpr3 as lpr3

# 在车牌图片上绘制识别结果
# 中文字体加载
font_ch = ImageFont.truetype("./static/font/platech.ttf", 20, 0)


def draw_plate_on_image(img, box, text, font):
    x1, y1, x2, y2 = box
    cv2.rectangle(img, (x1, y1), (x2, y2), (139, 139, 102), 2, cv2.LINE_AA)
    cv2.rectangle(img, (x1, y1 - 20), (x2, y1), (139, 139, 102), -1)
    data = Image.fromarray(img)
    draw = ImageDraw.Draw(data)
    draw.text((x1 + 1, y1 - 18), text, (255, 255, 255), font=font)
    res = np.asarray(data)

    return res


def create_app(config_name):
    # 创建 Flask 应用对象
    app = Flask(__name__)

    # 根据配置名称加载相应的配置类
    app.config.from_object(config_by_name[config_name])

    @app.route('/')
    def hello_world():
        return 'Hello, World!'

    # 注册页面
    @app.route('/register', methods=['GET', 'POST'])
    def show_register():
        if request.method == 'POST':
            username = request.form['username']
            email = request.form['email']
            password = request.form['password']
            confirm_password = request.form['confirm_password']
            captcha = request.form['captcha']

            # 添加验证码验证逻辑
            if captcha != '5374':
                return "验证码错误"

            if password != confirm_password:
                return "两次输入的密码不一致"

            result = create_user(username, email, password)
            return result

        return render_template('register.html')

    # 登录页面
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            # 在这里处理用户提交的登录表单数据
            email = request.form.get('email')
            password = request.form.get('password')
            user = sql_login(email, password)
            if user:
                # 登录成功，可以将用户信息存储在 session 中等
                flash('登录成功', 'success')  # 使用 Flask 的消息闪现功能
                return redirect('plate_re')
            else:
                flash('用户名或密码错误', 'error')
                return render_template('login.html')

        # 如果是 GET 请求，直接渲染登录页面
        return render_template('login.html')

    # 识别车牌页面
    @app.route('/plate_re', methods=['GET', 'POST'])
    def plate_re():
        plate_number = None
        confidence = None
        image_path = None
        image_path2 = None

        if request.method == 'POST':
            if 'image_file' not in request.files:
                return "未选择图像文件"

            try:
                image_file = request.files['image_file']
                if image_file:
                    # 保存上传的图像文件
                    image_path = "static/images/uploaded_image.png"
                    image_file.save(image_path)
                    image = cv2.imread(image_path)

                    # 执行识别算法
                    catcher = lpr3.LicensePlateCatcher(detect_level=lpr3.DETECT_LEVEL_HIGH)
                    results = catcher(image)

                    if results:
                        for code, confidence, type_idx, box in results:
                            # 解析数据并绘制
                            text = f"{code} - {confidence:.2f}"
                            image = draw_plate_on_image(image, box, text, font=font_ch)
                            image_path2 = "static/images/recognized_image.png"
                            cv2.imwrite("static/images/recognized_image.png", image)
                        code, confidence, _, _ = results[0]
                        plate_number = code
                    else:
                        plate_number = "未识别到车牌"

                return render_template('plate_re.html', image_path=image_path, image_path2=image_path2,
                                       plate_number=plate_number,
                                       confidence=confidence)
            except Exception as e:
                return str(e)

        return render_template('plate_re.html', image_path=image_path, plate_number=plate_number, confidence=confidence)

    # 展示识别信息的页面
    @app.route('/plate_display')
    def plate_recognition():
        try:
            # 连接数据库
            cursor, db = sql_connection()

            # 查询车牌识别结果数据
            cursor.execute("SELECT * FROM car_plate")
            plate_recognition_data = cursor.fetchall()
            if plate_recognition_data is None:
                return "表中暂无数据"

            # 关闭数据库连接
            db.close()

            # 渲染 HTML 模板并传递数据
            return render_template('plate_display.html', plate_recognition_data=plate_recognition_data)
        except Exception as e:
            return str(e)

    return app
