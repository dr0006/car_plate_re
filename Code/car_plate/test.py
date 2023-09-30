import cv2
import numpy as np


# 拉伸图像，进行等比缩放
def stretch(img):
    img_max = float(img.max())
    img_min = float(img.min())
    for i in range(img.shape[0]):
        for j in range(img.shape[1]):
            img[i, j] = (255 / (img_max - img_min)) * img[i, j] - (255 * img_min) / (img_max - img_min)
    return img


# 阈值处理
def dobinaryzation(_):
    ret, threshold = cv2.threshold(_, 100, 255, cv2.THRESH_BINARY)  # THRESH_BINARY_INV
    return threshold


# 寻找某区域最大外接矩形框4点坐标
def find_retangle(contour):
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
        rect = find_retangle(contour)

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


def find_license(img):
    """
    首先对输入图像进行了一系列预处理步骤，包括图像压缩、灰度转换、灰度拉伸、开运算等。
    然后，使用Canny边缘检测算子进行边缘检测。
    接着，进行了闭运算和再次开运算，用于连接和消除小区域。
    最后，调用 locate_license 方法定位车牌位置。
    :param img:
    :return: 车牌位置矩阵rect和原图像img
    """
    """预处理"""
    # 压缩图像
    a = 400 * img.shape[0] / img.shape[1]
    a = int(a)
    img = cv2.resize(img, (400, a))
    print("cv2.resize")
    cv2.imshow('resize', img)
    cv2.waitKey(0)

    # RGB转灰色
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    print("cv2.cvtColor,COLOR_BGR2GRAY")
    cv2.imshow('gray', gray)
    cv2.waitKey(0)

    # 灰度拉伸
    stretched = stretch(gray)
    print("stretched自定义函数，灰度拉伸")
    cv2.imshow('stretched', stretched)
    cv2.waitKey()

    # 进行开运算，用来去除噪声
    r = 16
    h = w = r * 2 + 1
    kernel = np.ones(shape=[h, w], dtype=np.uint8)
    # cv2.circle(kernel, (r, r), r, -1, -1)
    opening = cv2.morphologyEx(stretched, cv2.MORPH_OPEN, kernel)
    print("cv2.morphologyEx,进行开运算，用来去除噪声")
    cv2.imshow('opening', opening)
    cv2.waitKey()

    # 将灰度拉伸后的图和开运算后的图的差的绝对值输出
    strt = cv2.absdiff(stretched, opening)
    print("cv2.absdiff,将灰度拉伸后的图和开运算后的图的差的绝对值输出")
    cv2.imshow('strt', strt)
    cv2.waitKey()

    # 图像二值化
    binary = dobinaryzation(strt)
    print("图像二值化")
    cv2.imshow('binary', binary)
    cv2.waitKey()

    # Canny算子进行边缘检测
    canny = cv2.Canny(binary, binary.shape[0], binary.shape[1])
    print("Canny算子进行边缘检测")
    cv2.imshow('canny', canny)
    cv2.waitKey()

    '''消除小区域，连通大区域'''
    # 进行闭运算
    kernel = np.ones(shape=[5, 19], dtype=np.uint8)
    closing = cv2.morphologyEx(canny, cv2.MORPH_CLOSE, kernel)
    print("进行闭运算")
    cv2.imshow('closeing', closing)
    cv2.waitKey()

    # 进行开运算
    opening = cv2.morphologyEx(closing, cv2.MORPH_OPEN, kernel)
    print("进行开运算")
    cv2.imshow('opening', opening)
    cv2.waitKey()

    # 再次进行开运算
    kernel = np.ones(shape=(11, 5), dtype=np.uint8)
    opening = cv2.morphologyEx(opening, cv2.MORPH_OPEN, kernel)
    print("再次进行开运算")
    cv2.imshow('last', opening)

    # 消除小区域，定位车牌位置
    rect = locate_license(opening, img)
    return rect, img


if __name__ == '__main__':
    # im_name = r"./images/川A88888.jpg"
    im_name = r'./images/粤AAB457.JPG'
    orgimg = cv2.imdecode(np.fromfile(im_name, dtype=np.uint8), -1)  # 解决图片带中文路径报错
    img1 = orgimg.copy()
    rect, img = find_license(orgimg)
    cv2.rectangle(img, (rect[0], rect[1]), (rect[2], rect[3]), (0, 255, 0), 2)
    print("车牌矩阵", rect)
    cv2.imshow('img', img)
    cv2.waitKey()
    cv2.destroyAllWindows()
