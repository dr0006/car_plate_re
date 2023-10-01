# -*- coding: utf-8 -*-
"""
@File  : app.py
@author: FxDr
@Time  : 2023/09/30 15:38
@Description:
"""
import time

from flask import Flask, render_template, request, redirect, session, url_for
from functools import wraps

# 配置文件和sql相关操作
from config import config_by_name
from sql_car import create_user, sql_login, sql_connection, sql_reload

# 导入车牌识别代码
# from plate_re import lpr3_re, license_plate_re
from plate_re import lpr3_re


def login_required(view_func):
    """
    自定义装饰器，要求登录信息才可访问
    只需在路由下方添加@login_required即可
    超过三十分钟要求重新登陆
    :param view_func:
    :return:
    """

    @wraps(view_func)
    def wrapper(*args, **kwargs):
        if 'logged_in' in session and session['logged_in']:
            # 检查上次活动时间是否已超过30分钟
            last_activity_time = session.get('last_activity_time')
            if last_activity_time is None or (last_activity_time + 1800) >= int(time.time()):
                session['last_activity_time'] = int(time.time())  # 更新活动时间
                return view_func(*args, **kwargs)
            else:
                return redirect(url_for('login'))  # 超过30分钟需要重新登录
        else:
            return redirect(url_for('login'))  # 未登录时重定向到登录页面

    return wrapper


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
            print(result)
            if result is True:
                return redirect('/login')
            else:
                return 'Error:该邮箱地址已经注册'

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
                # 在会话中设置用户登录状态
                session['logged_in'] = True
                session['last_activity_time'] = int(time.time())
                session['user_email'] = email
                return redirect('plate_re')
            else:
                # 用户名或密码错误
                alert_script = '''
                <script>
                    // 页面加载时触发弹窗
                    window.onload = function() {
                        alert("用户名或密码错误！");
                        //重定向
                        window.location.href = '/login'
                    };
                </script>
                '''
                return alert_script
                # return render_template('login.html')

        # 如果是 GET 请求，直接渲染登录页面
        return render_template('login.html')

    # 退出登录路由
    @app.route('/plate_re/logout')
    def logout():
        # 清除会话中的登录状态和活动时间
        session.pop('logged_in', None)
        session.pop('last_activity_time', None)
        alert_script = '''
                <script>
                    // 页面加载时触发弹窗
                    window.onload = function() {
                        alert("Logged out successfully!");
                        //重定向
                        window.location.href = '/login'
                    };
                </script>
                '''
        return alert_script  # 'Logged out successfully!'

    # 识别车牌页面lpr3
    @app.route('/plate_re', methods=['GET', 'POST'])
    @login_required
    def plate_re():
        plate_dict = {}
        plate_number = None
        confidence = None
        image_path = None

        if request.method == 'POST':
            if 'image_file' not in request.files:
                return "未选择图像文件"

            try:
                image_file = request.files['image_file']
                if image_file:
                    # 保存上传的图像文件
                    image_path = "static/images/uploaded_image.png"
                    image_file.save(image_path)
                    plate_dict = lpr3_re(image_path)

                return render_template('plate_re.html', image_path=plate_dict['path1'], image_path2=plate_dict['path2'],
                                       plate_number=plate_dict['code'],
                                       confidence=plate_dict['confidence'])
            except Exception as e:
                return str(e)

        return render_template('plate_re.html', image_path=image_path, plate_number=plate_number, confidence=confidence)

    # 上传识别记录到数据库
    @app.route('/plate_re/uploadBT', methods=['GET'])
    @login_required
    def upload():
        user_email = session.get('user_email')  # 获得登录用户的邮箱名
        plate_number = request.args.get('plate_number')
        confidence = request.args.get('confidence')
        flag = sql_reload(user_email, plate_number, confidence)  # flag布尔值判断是否上传成功
        success_script = '''
                <script>
                    // 页面加载时触发弹窗
                    window.onload = function() {
                        alert("successfully!！");
                        //重定向
                        window.location.href = '/plate_re'
                    };
                </script>
                '''
        failure_script = '''
                <script>
                    // 页面加载时触发弹窗
                    window.onload = function() {
                        alert("上传失败");
                        //重定向
                        window.location.href = '/plate_re'
                    };
                </script>
                '''
        if flag:
            return success_script
        else:
            return failure_script

    # 展示识别信息的页面
    @app.route('/plate_re/plate_display')
    @login_required
    def plate_recognition():
        user_email = session['user_email']
        try:
            # 连接数据库
            cursor, db = sql_connection()

            # 查询车牌识别结果数据
            cursor.execute("SELECT * FROM car_plate WHERE user_email = %s", (user_email,))
            plate_recognition_data = cursor.fetchall()
            if plate_recognition_data is None:
                return "表中暂无数据"
            # 关闭数据库连接
            db.close()
            # print(plate_recognition_data)

            # 渲染 HTML 模板并传递数据
            return render_template('plate_display.html', datas=plate_recognition_data)
        except Exception as e:
            return str(e)

    # 弃用
    # # 车牌识别页面,license_plate_re
    # @app.route('/plate_re2', methods=['GET', 'POST'])
    # @login_required
    # def plate_re2():
    #     plate_dict = {}  # 保存plate_re,license_plate_re返回的结果
    #     plate_number = None
    #     confidence = None
    #     image_path = None  # 保存上传的图片地址
    #     # img_path_dict = {}  # 保存处理之后的tmp文件夹内的图片
    #
    #     if request.method == 'POST':
    #         if 'image_file' not in request.files:
    #             return "未选择图像文件"
    #
    #         try:
    #             image_file = request.files['image_file']
    #             if image_file:
    #                 # 保存上传的图像文件
    #                 image_path = "static/images/uploaded_image2.png"
    #                 image_file.save(image_path)
    #                 plate_dict = license_plate_re(image_path)
    #
    #             return render_template('plate_re2.html', image_path=plate_dict['path1'],
    #                                    image_path2=plate_dict['path2'],
    #                                    plate_number=plate_dict['plate_str'],
    #                                    plate_color=plate_dict['plate_color'],
    #                                    flag=plate_dict['flag'])
    #         except Exception as e:
    #             return str(e)
    #
    #     return render_template('plate_re2.html', image_path=image_path, plate_number=plate_number,
    #                            confidence=confidence)

    return app
