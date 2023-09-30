# -*- coding: utf-8 -*-
"""
@File  : main.py
@author: FxDr
@Time  : 2023/09/29 5:50
@Description:
"""
from tools import ChineseText

import numpy as np
from matplotlib import pyplot as plt
from paddleocr import PaddleOCR
import cv2


# 利用paddelOCR进行文字扫描，并输出结果
def text_scan(img_path):
    ocr = PaddleOCR(use_angle_cls=True, use_gpu=False)
    result = ocr.ocr(img_path, cls=True)
    return result


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
    cv2.imshow("gray", gray)
    cv2.waitKey(0)
    return gray


# 图像尺寸变换
def img_resize(img):
    a = 400 * img.shape[0] / img.shape[1]
    a = int(a)
    img = cv2.resize(img, (400, a))
    cv2.imshow("img_resize", img)
    cv2.waitKey(0)
    return img


# Sobel检测,x方向上的边缘检测（增强边缘信息）
def Sobel_detect(img):
    Sobel_x = cv2.Sobel(img, cv2.CV_16S, 1, 0)
    absX = cv2.convertScaleAbs(Sobel_x)
    cv2.imshow("Sobel_detect", absX)
    return absX


# 寻找某区域最大外接矩形框4点坐标
def find_rectangle(contour):
    y, x = [], []
    for p in contour:
        y.append(p[0][0])
        x.append(p[0][1])
    return [min(y), min(x), max(y), max(x)]


def locate_license(img, orgimg):
    """
    定位车牌位置
    :param img:
    :param orgimg:
    :return: 返回最像车牌的区域坐标
    """
    # 寻找轮廓
    contours, hierarchies = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

    # 存储候选车牌区域的列表
    candidate_blocks = []

    # 遍历所有轮廓
    for contour in contours:
        # 计算轮廓的外接矩形
        rect = find_rectangle(contour)

        # 计算外接矩形的面积和长宽比
        area = (rect[2] - rect[0]) * (rect[3] - rect[1])
        aspect_ratio = (rect[2] - rect[0]) / (rect[3] - rect[1])

        # 存储候选车牌区域的矩形、面积和长宽比
        candidate_blocks.append([rect, area, aspect_ratio])

    # 选取面积最大的3个区域作为候选车牌
    candidate_blocks = sorted(candidate_blocks, key=lambda b: b[1])[-3:]

    # 使用颜色识别判断出最像车牌的区域
    max_weight, max_index = 0, -1

    # 判断每个候选车牌区域的颜色
    for i, block_info in enumerate(candidate_blocks):
        rect, area, _ = block_info
        block = orgimg[rect[1]:rect[3], rect[0]:rect[2]]

        # 转换为HSV颜色空间
        hsv = cv2.cvtColor(block, cv2.COLOR_BGR2HSV)

        # 定义蓝色车牌的颜色范围
        lower_blue = np.array([100, 50, 50])
        upper_blue = np.array([140, 255, 255])

        # 使用阈值构建掩模
        mask = cv2.inRange(hsv, lower_blue, upper_blue)

        # 统计掩模中像素值为255的数量，作为权值
        weight = np.sum(mask / 255)

        # 选取最大权值的区域作为最像车牌的区域
        if weight > max_weight:
            max_index = i
            max_weight = weight

    # 返回最像车牌的区域坐标
    return candidate_blocks[max_index][0]


# 图像预处理+车牌轮廓位置检测
def find_license_points(img, org_img):
    # 1. 对输入图像进行灰度化和高斯模糊
    gray = gray_gauss(img)

    # 2. 使用Sobel算子进行边缘检测
    sobel = Sobel_detect(gray)

    # 3. 使用OTSU阈值法进行图像二值化
    ret, threshold = cv2.threshold(sobel, 0, 255, cv2.THRESH_OTSU)

    # 4. 构建水平方向的矩形核，进行闭运算以连接车牌区域的断开部分
    kernel_x = cv2.getStructuringElement(cv2.MORPH_RECT, (30, 10))
    closing = cv2.morphologyEx(threshold, cv2.MORPH_CLOSE, kernel_x, iterations=1)

    # 5. 构建水平和垂直方向的矩形核，对图像进行膨胀和腐蚀操作
    kernel_x = cv2.getStructuringElement(cv2.MORPH_RECT, (50, 1))
    kernel_y = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 20))
    img = cv2.dilate(closing, kernel_x)
    img = cv2.erode(img, kernel_x)
    img = cv2.erode(img, kernel_y)
    img = cv2.dilate(img, kernel_y)

    # 6. 使用中值滤波对图像进行平滑处理
    blur = cv2.medianBlur(img, 15)

    # 7. 定位车牌区域
    rect = locate_license(blur, org_img)

    # 8. 在显示图像上绘制车牌区域（仅用于调试）
    cv2.imshow("license", blur)
    cv2.waitKey(0)

    # 9. 返回车牌区域的位置和处理后的图像
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
    # img = cv2.imread(r'./images/captcha.png')
    # im_name = r'./images/川A88888.jpg'  # 正常
    # im_name = r'./images/川A09X20.jpg' # 正常
    # im_name = r'./images/皖P77222.jpg'  # 未正确找到车牌轮廓
    im_name = r'./images/粤AAB457.JPG'  # OCR是否返回结果? [None]
    # im_name = r'./images/img_4.png'
    img = cv2.imdecode(np.fromfile(im_name, dtype=np.uint8), -1)  # 解决图片带中文路径报错
    img = img_resize(img)
    oriimg = img.copy()
    rect, img = find_license_points(img, oriimg)

    if rect is not None:
        result = segment_characters(rect, oriimg)
        # 在图像上绘制车牌号
        text_x = rect[0] + 20  # 调整文本的X坐标
        text_y = rect[1] - 30  # 调整文本的Y坐标
        # text_color = (0, 255, 0)  # 文本颜色为绿色
        text_color = (0, 0, 255)  # 文本颜色
        text = ""
        confidence = ""
        # print("result", result)
        for lst in result:
            try:
                text, confidence = lst[0][1]
                print("车牌为：{}\n置信度为:{}".format(text, confidence))
            except:
                print("OCR是否返回结果?", result)
            text = text[:2] + text[3:]  # 去掉车牌信息中的 · 点，因为绘制不出来，显示为方框

        cv2.rectangle(oriimg, (rect[0], rect[1]), (rect[2], rect[3]), (0, 255, 0), 2)
        oriimg = ChineseText.cv2img_add_text(oriimg, text, text_x, text_y, text_color=text_color)
        cv2.imshow('oriimg', oriimg)
        cv2.waitKey()
    else:
        print("未找到车牌轮廓")
