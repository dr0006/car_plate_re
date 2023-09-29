# 导入必要的模块和依赖项
from .config.settings import onnx_runtime_config as ort_cfg  # 导入 ONNX 模型配置
from .inference.pipeline import LPRMultiTaskPipeline  # 导入车牌识别的多任务管道
from .common.typedef import *  # 导入常用的类型定义
from os.path import join  # 导入用于拼接文件路径的函数
from .config.settings import _DEFAULT_FOLDER_  # 导入默认模型下载文件夹路径
from .config.configuration import initialization  # 导入初始化函数

# 初始化 HyperLPR3 模型配置
initialization()


# 创建 LicensePlateCatcher 类，用于车牌识别
class LicensePlateCatcher(object):

    # 构造函数，用于初始化车牌识别器
    def __init__(self,
                 inference: int = INFER_ONNX_RUNTIME,  # 推断模式，默认使用 ONNX 运行时
                 folder: str = _DEFAULT_FOLDER_,  # 模型存储文件夹路径，默认为默认文件夹
                 detect_level: int = DETECT_LEVEL_LOW,  # 车牌检测级别，默认为低级
                 logger_level: int = 3,  # 日志记录级别，默认为 3
                 full_result: bool = False):  # 是否获取完整的识别结果，默认为 False

        # 检查是否选择了 ONNX 运行时
        if inference == INFER_ONNX_RUNTIME:
            from hyperlpr3.inference.multitask_detect import MultiTaskDetectorORT  # 导入车牌检测器类
            from hyperlpr3.inference.recognition import PPRCNNRecognitionORT  # 导入车牌识别器类
            from hyperlpr3.inference.classification import ClassificationORT  # 导入车牌分类器类
            import onnxruntime as ort  # 导入 ONNX 运行时库
            ort.set_default_logger_severity(logger_level)  # 设置 ONNX 运行时的日志级别

            # 根据选择的车牌检测级别，初始化相应的检测器模型
            if detect_level == DETECT_LEVEL_LOW:
                det = MultiTaskDetectorORT(join(folder, ort_cfg['det_model_path_320x']), input_size=(320, 320))
            elif detect_level == DETECT_LEVEL_HIGH:
                det = MultiTaskDetectorORT(join(folder, ort_cfg['det_model_path_640x']), input_size=(640, 640))
            else:
                raise NotImplemented  # 抛出未实现异常

            rec = PPRCNNRecognitionORT(join(folder, ort_cfg['rec_model_path']), input_size=(48, 160))  # 初始化识别器模型
            cls = ClassificationORT(join(folder, ort_cfg['cls_model_path']), input_size=(96, 96))  # 初始化分类器模型

            # 创建车牌识别的多任务管道，包括检测、识别和分类
            self.pipeline = LPRMultiTaskPipeline(detector=det, recognizer=rec, classifier=cls, full_result=full_result)
        else:
            raise NotImplemented  # 抛出未实现异常

    # 调用方法，用于对输入图像进行车牌识别
    def __call__(self, image: np.ndarray, *args, **kwargs):
        return self.pipeline(image)  # 返回识别结果
