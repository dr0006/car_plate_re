# -*- coding: utf-8 -*-
"""
@File  : 6.py
@author: FxDr
@Time  : 2023/09/28 23:49
@Description:
"""
import json
import cv2
import numpy as np

# 1. 解析JSON文件
json_file_path = 'data/carplate/train/via_project_carplate_train.json'  # 请替换为你的JSON文件路径
with open(json_file_path, 'r', encoding='UTF-8') as json_file:
    data = json.load(json_file)

# 2. 检查JSON结构并访问图像数据和车牌坐标
if '_via_img_metadata' in data:
    img_metadata = data['_via_img_metadata']

    # 存储图像和车牌坐标的列表
    images = []
    plates = []
    files = []
    for image_id, image_info in img_metadata.items():
        filename = r'data/carplate/train/' + image_info["filename"]
        regions = image_info["regions"]

        # 加载图像
        # image = cv2.imread(filename)
        image = cv2.imdecode(np.fromfile(filename, dtype=np.uint8), -1)
        print(filename)
        files.append(filename)

        # 提取车牌坐标
        for region in regions:
            points_x = region["shape_attributes"]["all_points_x"]
            points_y = region["shape_attributes"]["all_points_y"]

            # 创建车牌区域的坐标
            plate_coordinates = np.array(list(zip(points_x, points_y)), dtype=np.int32)

            # 将图像和车牌坐标添加到列表
            images.append(image)
            plates.append(plate_coordinates)

    # 在此处进行数据预处理，例如图像调整大小、归一化等
    # 你可以根据模型的要求进行适当的预处理操作
    # 例如，将图像和车牌坐标转换为模型所需的格式

    # 打印示例数据
    print(f"总共加载了{len(images)}张图像和{len(plates)}个车牌坐标。")
    cv2.waitKey(0)
    print(len(files))

else:
    print("'_via_img_metadata' not found in the JSON file.")
