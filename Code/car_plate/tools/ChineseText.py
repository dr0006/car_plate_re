# -*- coding: utf-8 -*-
"""
@File  : ChineseText.py
@author: FxDr
@Time  : 2023/09/29 15:25
@Description: 这个模块用来在图像上绘制文字中文
"""
# 解决中文乱码

import cv2
import numpy
from PIL import Image, ImageDraw, ImageFont


def cv2img_add_text(img, text, left, top, text_color=(0, 255, 0), text_size=20):
    if isinstance(img, numpy.ndarray):  # 判断是否OpenCV图片类型
        img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(img)
    fontText = ImageFont.truetype(
        r"X:\Coding\Github\car_plate_re\font\platech.ttf", text_size, encoding="utf-8")
    draw.text((left, top), text, text_color, font=fontText)
    return cv2.cvtColor(numpy.asarray(img), cv2.COLOR_RGB2BGR)
