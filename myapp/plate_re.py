# -*- coding: utf-8 -*-
"""
@File  : plate_re.py
@author: FxDr
@Time  : 2023/09/30 23:37
@Description:车牌识别相关
"""
import cv2
# 导入Code相关
from Code.license_plate_re import img_function as predict
from Code.license_plate_re import img_math as img_math

# 导入lpr3相关
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import hyperlpr3 as lpr3

# 中文字体加载
font_ch = ImageFont.truetype("./static/font/platech.ttf", 20, 0)


# 在车牌图片上绘制识别结果
def draw_plate_on_image(img, box, text, font):
    x1, y1, x2, y2 = box
    cv2.rectangle(img, (x1, y1), (x2, y2), (139, 139, 102), 2, cv2.LINE_AA)
    cv2.rectangle(img, (x1, y1 - 20), (x2, y1), (139, 139, 102), -1)
    data = Image.fromarray(img)
    draw = ImageDraw.Draw(data)
    draw.text((x1 + 1, y1 - 18), text, (255, 255, 255), font=font)
    res = np.asarray(data)

    return res


# lpr3库车牌识别
def lpr3_re(image_path):
    image_path2 = None
    confidence = None
    image = cv2.imread(image_path)

    # 执行lpr3识别算法
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
    plate_dict = {'path1': image_path, 'path2': image_path2, 'code': plate_number, 'confidence': confidence}
    return plate_dict


# 弃用
# def license_plate_re(pic_path):
#     image_path2 = None
#     predictor = predict.CardPredictor()
#     predictor.train_svm()
#     img_bgr = img_math.img_read(pic_path)  # 读取图片可带中文路径
#     # cv2.imshow("img", img_bgr)
#     # cv2.waitKey(0)
#
#     first_img, oldimg = predictor.img_first_pre(img_bgr)
#
#     plate_str, roi, plate_color = predictor.img_only_color(oldimg,
#                                                            oldimg, first_img)
#
#     # print("车牌颜色:{}\n车牌为{}".format(plate_color, plate_str))
#     if roi is not None and roi.shape[0] > 0 and roi.shape[1] > 0:
#         print("车牌区域有效")
#         image_path2 = "static/images/recognized_image2.png"  # 裁剪的车牌图片的地址
#         cv2.imwrite("static/images/recognized_image2.png", roi)
#         flag = True
#     else:
#         print("无效的车牌区域")
#         flag = False
#     car_dict = {'plate_color': plate_color, 'plate_str': plate_str, 'path1': pic_path, 'path2': image_path2,
#                 'flag': flag}
#     return car_dict
