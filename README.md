# car_plate_re

车牌识别

**Fxx**

--------------------------------

## hyperlpr3库

- opencv-python (>3.3)
- onnxruntime (>1.8.1)
- fastapi (0.92.0)
- uvicorn (0.20.0)
- loguru (0.6.0)
- python-multipart
- tqdm
- requests

```bash
raise ValueError(
ValueError: This ORT build has ['AzureExecutionProvider', 'CPUExecutionProvider'] enabled. Since ORT 1.9, you are
required to explicitly set the providers parameter when instantiating InferenceSession. For example,
onnxruntime.InferenceSession(..., providers=['AzureExecutionProvider', 'CPUExecutionProvider'], ...)
```

> 当onnxruntime版本较新的时候，我发现运行报错,所有我装的是1.8.1


--------------------------------------------------

## 简单车牌识别模型训练

> 标注工具使用VGG Image Annotator (VIA)，就是一个网页程序，可以导入图片，使用多边形标注，标注好了以后，导出json

- Code lpr3代码部分
- data
  - ann 用于字符识别的数据集，包含分隔好的单个车牌汉子、字母和数字
  - carplate 用于车牌定位的数据集，要收集250张车辆图片，200张用于训练，50张用于测试，然后在这些图片上标注出车牌区域
- .gitignore 忽略上传到git的文件夹
- font 中文字体