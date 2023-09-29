import os
import sys

# _DEFAULT_FOLDER_ 模型下载的所在文件夹

_MODEL_VERSION_ = "20230229"

if 'win32' in sys.platform:
    _DEFAULT_FOLDER_ = os.path.join(os.environ['HOMEPATH'], ".hyperlpr3")
else:
    _DEFAULT_FOLDER_ = os.path.join(os.environ['HOME'], ".hyperlpr3")
print(_DEFAULT_FOLDER_)  # 下载到了我的X盘
# X:\Users\lenovo\.hyperlpr3

_ONLINE_URL_ = "http://hyperlpr.tunm.top/raw/"

onnx_runtime_config = dict(
    det_model_path_320x=os.path.join(_MODEL_VERSION_, "onnx", "y5fu_320x_sim.onnx"),
    det_model_path_640x=os.path.join(_MODEL_VERSION_, "onnx", "y5fu_640x_sim.onnx"),
    rec_model_path=os.path.join(_MODEL_VERSION_, "onnx", "rpv3_mdict_160_r3.onnx"),
    cls_model_path=os.path.join(_MODEL_VERSION_, "onnx", "litemodel_cls_96x_r1.onnx"),
)

onnx_model_maps = ["det_model_path_320x", "det_model_path_640x", "rec_model_path", "cls_model_path"]
