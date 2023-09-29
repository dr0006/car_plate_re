# -*- coding: utf-8 -*-
"""
@File  : main.py
@author: FxDr
@Time  : 2023/09/29 5:50
@Description:
"""
from tools import ChineseText

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from matplotlib import pyplot as plt
from paddleocr import PaddleOCR
import cv2


# 利用paddelOCR进行文字扫描，并输出结果
def text_scan(img_path):
    ocr = PaddleOCR(use_angle_cls=True, use_gpu=False)
    result = ocr.ocr(img_path, cls=True)
    return result


# 在图片中写入将车牌信息
def infor_write(img, rect, result):
    if result:
        text = result[0][1][0] if result[0][1] else "No characters detected"
    else:
        text = "No characters detected"
    # text = result[1][0]
    cv2img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    pilimg = Image.fromarray(cv2img)
    draw = ImageDraw.Draw(pilimg)
    # font = ImageFont.truetype("simhei.ttf", 20, encoding="utf-8")
    font = ImageFont.truetype(r"X:\Coding\Github\car_plate_re\font\platech.ttf", 20, encoding="utf-8")
    draw.text((rect[2], rect[1]), str(text), (0, 255, 0), font=font)
    cv2charimg = cv2.cvtColor(np.array(pilimg), cv2.COLOR_RGB2BGR)
    return cv2charimg


# plt显示彩色图片
def plt_show0(img):
    b, g, r = cv2.split(img)
    img = cv2.merge([r, g, b])
    plt.imshow(img)
    plt.show()


# plt显示灰度图片
def plt_show(img):
    plt.imshow(img, cmap='gray')
    plt.show()


# 图像去噪灰度处理
def gray_gauss(img):
    img = cv2.GaussianBlur(img, (1, 1), 0)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    return gray


# 图像尺寸变换
def img_resize(img):
    a = 400 * img.shape[0] / img.shape[1]
    a = int(a)
    img = cv2.resize(img, (400, a))
    return img


# Sobel检测,x方向上的边缘检测（增强边缘信息）
def Sobel_detect(img):
    Sobel_x = cv2.Sobel(img, cv2.CV_16S, 1, 0)
    absX = cv2.convertScaleAbs(Sobel_x)
    return absX


# 寻找某区域最大外接矩形框4点坐标
def find_rectangle(contour):
    y, x = [], []
    for p in contour:
        y.append(p[0][0])
        x.append(p[0][1])
    return [min(y), min(x), max(y), max(x)]


# 寻找并定位车牌轮廓位置
def locate_license(img, orgimg):
    blocks = []
    contours, hierarchy = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for c in contours:
        x, y, w, h = cv2.boundingRect(c)
        r = find_rectangle(c)
        a = (r[2] - r[0]) * (r[3] - r[1])  # r=[min(y),min(x),max(y),max(x)]
        s = (r[2] - r[0]) / (r[3] - r[1])
        # 根据轮廓形状特点，确定车牌的轮廓位置并截取图像
        if (w > (h * 3)) and (w < (h * 5)):
            # img=oriimg[y:y+h,x:x+w]
            # cv2.rectangle(oriimg, (x, y), (x+w, y+h), (0, 255, 0), 2)
            blocks.append([r, a, s])

    if not blocks:
        return None  # 如果没有找到符合条件的车牌轮廓，返回 None

    # 选出面积最大的3个区域
    blocks = sorted(blocks, key=lambda b: b[1])[-3:]  # 按照blocks第3个元素大小进行排序
    # 使用颜色识别判断出最像车牌的区域
    max_weight, max_index = 0, -1
    # 划分ROI区域
    for i in range(len(blocks)):
        b = orgimg[blocks[i][0][1]:blocks[i][0][3], blocks[i][0][0]:blocks[i][0][2]]
        # RGB转HSV
        hsv = cv2.cvtColor(b, cv2.COLOR_BGR2HSV)
        # 蓝色车牌范围
        lower = np.array([100, 50, 50])
        upper = np.array([140, 255, 255])
        # 根据阈值构建掩模
        mask = cv2.inRange(hsv, lower, upper)
        # 统计权值
        w1 = 0
        for m in mask:
            w1 += m / 255
        w2 = 0
        for w in w1:
            w2 += w
        # 选出最大权值的区域
        if w2 > max_weight:
            max_index = i
        max_weight = w2
    return blocks[max_index][0]


# 图像预处理+车牌轮廓位置检测
def find_license_points(img, org_img):
    guss = gray_gauss(img)
    sobel = Sobel_detect(guss)
    ret, threshold = cv2.threshold(sobel, 0, 255, cv2.THRESH_OTSU)
    kernel_x = cv2.getStructuringElement(cv2.MORPH_RECT, (30, 10))
    closing = cv2.morphologyEx(threshold, cv2.MORPH_CLOSE, kernel_x, iterations=1)
    kernel_x = cv2.getStructuringElement(cv2.MORPH_RECT, (50, 1))
    kernel_y = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 20))
    img = cv2.dilate(closing, kernel_x)
    img = cv2.erode(img, kernel_x)
    img = cv2.erode(img, kernel_y)
    img = cv2.dilate(img, kernel_y)
    blur = cv2.medianBlur(img, 15)
    rect = locate_license(blur, org_img)
    return rect, blur


# 车牌字符识别
def segment_characters(rect_list, org_img):
    img = org_img[rect_list[1]:rect_list[3], rect_list[0]:rect_list[2]]
    gray = gray_gauss(img)
    k1 = np.ones((1, 1), np.uint8)
    close = cv2.morphologyEx(gray, cv2.MORPH_CLOSE, k1)
    cv2.imwrite(r'./images/imwrite.jpg', close)
    res = text_scan(r'./images/imwrite.jpg')
    return res


# 主函数区
if __name__ == '__main__':
    img = cv2.imread(r'./images/img.png')
    img = img_resize(img)
    oriimg = img.copy()
    rect, img = find_license_points(img, oriimg)

    if rect is not None:
        result = segment_characters(rect, oriimg)
        # 在图像上绘制车牌号
        text_x = rect[0] + 10  # 调整文本的X坐标
        text_y = rect[1] + 10  # 调整文本的Y坐标
        text_color = (0, 255, 0)  # 文本颜色为绿色
        text = ""
        confidence = ""
        for lst in result:
            text, confidence = lst[0][1]
            print("车牌为：{}\n置信度为:{}".format(text, confidence))
            oriimg = infor_write(oriimg, rect, lst)
        text = text[:2] + text[3:]  # 去掉车牌信息中的 · 点，因为绘制不出来，显示为方框
        oriimg = ChineseText.cv2img_add_text(oriimg, text, text_x, text_y)
        cv2.rectangle(oriimg, (rect[0], rect[1]), (rect[2], rect[3]), (0, 255, 0), 2)
        cv2.imshow('oriimg', oriimg)
        cv2.waitKey()
    else:
        print("未找到车牌轮廓")
