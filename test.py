# -*- coding: utf-8 -*-
"""
@File  : test.py
@author: FxDr
@Time  : 2023/09/29 0:19
@Description:
"""
import cv2
import numpy as np

# 解决cv读取中文图片报错
# img = cv2.imread(r"images/car4.jpg")
# img = cv2.imread(r"images/吉car4.jpg")
im_name = "images/吉car4.jpg"
img = cv2.imdecode(np.fromfile(im_name, dtype=np.uint8), -1)
cv2.imshow('img', img)
cv2.waitKey(0)
