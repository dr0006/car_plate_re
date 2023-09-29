# -*- coding: utf-8 -*-
"""
@File  : UI.py
@author: FxDr
@Time  : 2023/09/27 11:02
@Description:
"""

import sys
import cv2
import hyperlpr3 as lpr3  # hyperlpr3用来车牌识别
import numpy as np
from PIL import ImageFont, Image, ImageDraw
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QTextCursor, QImage
from PyQt5.QtWidgets import QApplication, QMainWindow, QHBoxLayout, QVBoxLayout, QPushButton, QLabel, QWidget, \
    QFileDialog, QTextEdit


class LicensePlateRecognitionApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.btn_select_file = None  # 选择文件按钮
        self.catcher = None
        self.image_path = None  # 图片路径
        self.font_ch = None  # 字体
        self.btn_recognize = None  # 识别按钮
        self.lbl_image = None  # 图片标签
        self.result_text = None  # 用于存储识别历史的文本
        self.initUI()

    def initUI(self):
        self.setWindowTitle("车牌识别")
        self.setGeometry(100, 100, 1000, 600)

        # 创建水平布局，分为左右两个部分
        hbox = QHBoxLayout()

        # 创建垂直布局，用于左侧部分
        left_layout = QVBoxLayout()

        # 创建一个中文字体
        self.font_ch = ImageFont.truetype("../.././font/platech.ttf", 20, 0)

        # 创建识别器
        self.catcher = lpr3.LicensePlateCatcher(detect_level=lpr3.DETECT_LEVEL_HIGH)

        # 创建一个水平布局，用于按钮
        button_layout = QHBoxLayout()

        # 创建选择文件按钮
        self.btn_select_file = QPushButton("选择本地图片")
        self.btn_select_file.clicked.connect(self.load_image)
        button_layout.addWidget(self.btn_select_file)

        # 创建识别按钮
        self.btn_recognize = QPushButton("识别车牌")
        self.btn_recognize.clicked.connect(self.recognize_license_plate)
        button_layout.addWidget(self.btn_recognize)

        # 添加按钮布局到左侧布局
        left_layout.addLayout(button_layout)

        # 创建一个文本显示区域，用于显示识别历史
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)  # 设置为只读
        self.result_text.setMinimumHeight(300)  # 设置最小高度

        # 添加左侧布局到水平布局
        hbox.addLayout(left_layout)

        # 添加文本显示区域到水平布局
        hbox.addWidget(self.result_text)

        # 创建显示图片的标签
        self.lbl_image = QLabel()
        hbox.addWidget(self.lbl_image)

        # 创建主窗口的中心部件
        central_widget = QWidget()
        central_widget.setLayout(hbox)
        self.setCentralWidget(central_widget)

        self.image_path = None

    def load_image(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        file_path, _ = QFileDialog.getOpenFileName(self, "选择图片", r"X:\Coding\study\python_PlateRecogntion\car_pic",
                                                   "Images (*.png *.jpg *.bmp *.jpeg);;All Files (*)", options=options)

        if file_path:
            self.image_path = file_path
            pixmap = self.load_image_as_pixmap(file_path)
            self.lbl_image.setPixmap(pixmap)

    def load_image_as_pixmap(self, image):
        if isinstance(image, np.ndarray):
            # 如果输入是 OpenCV 图像
            height, width, channel = image.shape
            bytes_per_line = 3 * width
            qImg = QImage(image.data, width, height, bytes_per_line, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(qImg)
        else:
            # 如果输入是文件路径
            pixmap = QPixmap(image)

        pixmap = pixmap.scaledToWidth(500, Qt.SmoothTransformation)
        return pixmap

    def recognize_license_plate(self):
        try:
            if self.image_path:
                # 读取图片
                # image = cv2.imread(self.image_path)
                image = cv2.imdecode(np.fromfile(self.image_path, dtype=np.uint8), -1)  # 解决中文路径报错

                # 执行识别算法
                results = self.catcher(image)
                recognized_plates = []

                for code, confidence, type_idx, box in results:
                    # 解析数据并绘制
                    text = f"{code} - {confidence:.2f}"
                    image = self.draw_plate_on_image(image, box, text)
                    recognized_plates.append(f"{code} - {confidence:.2f}")

                # 更新显示图片
                pixmap = self.load_image_as_pixmap(image)
                self.lbl_image.setPixmap(pixmap)

                # 更新识别历史文本
                self.result_text.append("\n".join(recognized_plates))
                self.result_text.moveCursor(QTextCursor.End)  # 将文本滚动到末尾
                self.result_text.ensureCursorVisible()  # 确保光标可见
                self.result_text.setStyleSheet("font-weight: bold; font-style: italic;font-size:20px")
        except Exception as e:
            print(str(e))

    def draw_plate_on_image(self, img, box, text):
        x1, y1, x2, y2 = box
        cv2.rectangle(img, (x1, y1), (x2, y2), (139, 139, 102), 2, cv2.LINE_AA)
        cv2.rectangle(img, (x1, y1 - 20), (x2, y1), (139, 139, 102), -1)
        data = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        draw = ImageDraw.Draw(data)
        draw.text((x1 + 1, y1 - 18), text, (255, 255, 255), font=self.font_ch)
        res = np.asarray(data)
        return res


def main():
    app = QApplication(sys.argv)
    window = LicensePlateRecognitionApp()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
