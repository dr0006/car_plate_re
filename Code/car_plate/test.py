import cv2
import numpy as np


# 拉伸图像，进行等比缩放
def stretch(img):
    max = float(img.max())
    min = float(img.min())
    for i in range(img.shape[0]):
        for j in range(img.shape[1]):
            img[i, j] = (255 / (max - min)) * img[i, j] - (255 * min) / (max - min)
    return img


# 阈值处理
def dobinaryzation(img):
    max = float(img.max())
    min = float(img.min())
    x = max - ((max - min) / 2)
    ret, threshold = cv2.threshold(img, 100, 255, cv2.THRESH_BINARY)  # THRESH_BINARY_INV
    return threshold


# 寻找某区域最大外接矩形框4点坐标
def find_retangle(contour):
    y, x = [], []
    for p in contour:
        y.append(p[0][0])
        x.append(p[0][1])
    return [min(y), min(x), max(y), max(x)]


# 定位车牌位置
def locate_license(img, orgimg):
    contours, hierachy = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

    blocks = []
    for c in contours:
        # 绘制出所有边框进行对比
        # x, y, w, h = cv2.boundingRect(c)
        # cv2.rectangle(img1, (x, y), (x + w, y + h), (0, 255, 0), 1)
        # 找出轮廓的左上和右下点，计算出其面积和长宽比
        r = find_retangle(c)
        a = (r[2] - r[0]) * (r[3] - r[1])  # [min(y),min(x),max(y),max(x)]
        s = (r[2] - r[0]) / (r[3] - r[1])
        # cv2.rectangle(img,(r[1],r[0]),(r[3],r[2]),(255,255,0),3 )
        blocks.append([r, a, s])
    # 选出面积最大的3个区域
    blocks = sorted(blocks, key=lambda b: b[1])[-3:]  # 按照blocks第3个元素大小进行排序
    # 使用颜色识别判断出最像车牌的区域
    maxweight, maxindex = 0, -1
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
        if w2 > maxweight:
            maxindex = i
        maxweight = w2
    return blocks[maxindex][0]


def find_license(img):
    """预处理"""
    # 压缩图像
    a = 400 * img.shape[0] / img.shape[1]
    a = int(a)
    img = cv2.resize(img, (400, a))
    # cv2.imshow('img',img)
    # cv2.waitKey(0)
    # RGB转灰色
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # cv2.imshow('gray',gray)
    # cv2.waitKey(0)
    # 灰度拉伸
    stretched = stretch(gray)
    # cv2.imshow('stretched',stretched)
    # cv2.waitKey()
    # 进行开运算，用来去除噪声
    r = 16
    h = w = r * 2 + 1
    kernel = np.ones(shape=[h, w], dtype=np.uint8)
    cv2.circle(kernel, (r, r), r, -1, -1)
    opening = cv2.morphologyEx(stretched, cv2.MORPH_OPEN, kernel)
    # cv2.imshow('opening',opening)
    # cv2.waitKey()
    # 将灰度拉伸后的图和开运算后的图的差的绝对值输出
    strt = cv2.absdiff(stretched, opening)
    # cv2.imshow('strt', strt)
    # cv2.waitKey()
    # 图像二值化
    binary = dobinaryzation(strt)
    # cv2.imshow('binary',binary)
    # cv2.waitKey()
    # Canny算子进行边缘检测
    canny = cv2.Canny(binary, binary.shape[0], binary.shape[1])
    # cv2.imshow('canny',canny)
    # cv2.waitKey()
    '''消除小区域，连通大区域'''
    # 进行闭运算
    kernel = np.ones(shape=[5, 19], dtype=np.uint8)
    closing = cv2.morphologyEx(canny, cv2.MORPH_CLOSE, kernel)
    # cv2.imshow('closeing',closing)
    # cv2.waitKey()
    # 进行开运算
    opening = cv2.morphologyEx(closing, cv2.MORPH_OPEN, kernel)
    # cv2.imshow('opening',opening)
    # cv2.waitKey()
    # 再次进行开运算
    kernel = np.ones(shape=(11, 5), dtype=np.uint8)
    opening = cv2.morphologyEx(opening, cv2.MORPH_OPEN, kernel)
    cv2.imshow('opening', opening)
    # 消除小区域，定位车牌位置
    rect = locate_license(opening, img)
    return rect, img


if __name__ == '__main__':
    orgimg = cv2.imread(r'images/img.png')
    img1 = orgimg.copy()
    rect, img = find_license(orgimg)
    cv2.rectangle(img, (rect[0], rect[1]), (rect[2], rect[3]), (0, 255, 0), 2)
    cv2.imshow('img', img)
    cv2.waitKey()
    cv2.destroyAllWindows()
