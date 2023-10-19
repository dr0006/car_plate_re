# -*- coding: utf-8 -*-
"""
@File  : test.py
@author: FxDr
@Time  : 2023/09/29 20:23
@Description:
"""
import cv2

import img_function as predict
import img_math as img_math


def pic(pic_path):
    predictor = predict.CardPredictor()  # 创建CardPredictor的实例
    predictor.train_svm()
    img_bgr = img_math.img_read(pic_path)  # 读取图片可带中文路径
    cv2.imshow("img", img_bgr)
    cv2.waitKey(0)
    # 图像的处理img_first_pre
    # :return:已经处理好的图像文件 原图像文件
    first_img, oldimg = predictor.img_first_pre(img_bgr)
    # cv2.imshow("first", first_img)
    # cv2.waitKey(0)

    # cv2.imshow("oldimg", oldimg)
    # cv2.waitKey(0)
    # img_only_color识别
    # :return: 识别到的字符、定位的车牌图像、车牌颜色
    plate_str, roi, plate_color = predictor.img_only_color(oldimg,
                                                           oldimg, first_img)

    print("车牌颜色:{}\n车牌为{}".format(plate_color, plate_str))
    # cv2.imshow("roi", roi)
    if roi is not None and roi.shape[0] > 0 and roi.shape[1] > 0:
        cv2.imshow("roi", roi)
        cv2.waitKey(0)
    else:
        print("无效的车牌区域")


# pic(r"./pic/川A88888.jpg") # 识别正确
pic(r"./pic/img_4.png")  # 识别正确
# pic(r"./pic/川A09X20.jpg")  # 识别不当 框出车牌但是不完全准确
# pic(r"./pic/粤AAB457.JPG")# 识别不当 无法找到车牌位置
# pic(r"./pic/皖P77222.jpg")  # 识别不当 找到车牌位置错误
