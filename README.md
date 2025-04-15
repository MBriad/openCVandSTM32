# YOLO物体检测应用

这是一个基于YOLOv4-tiny的实时物体检测应用程序，使用OpenCV和Python实现。该应用程序可以通过摄像头实时检测物体，并可以保存检测结果。

## 功能特点

- 使用YOLOv4-tiny进行实时物体检测
- 支持显示检测框、标签和置信度
- 显示FPS和推理时间等性能指标
- 错误处理和异常恢复机制
- 支持按键保存检测结果
- 支持自动保存检测到物体的帧
- 兼容不同版本的OpenCV

## 系统要求

- Python 3.6或更高版本
- OpenCV 4.2或更高版本
- NumPy
- 摄像头或视频输入设备

## 安装

1. 克隆或下载代码库
2. 安装所需依赖：
```
pip install opencv-python numpy
```
3. 下载YOLOv4-tiny模型文件：
   - `yolov4-tiny.weights`：预训练权重文件
   - `yolov4-tiny.cfg`：模型配置文件
   - `coco.names.txt`：类别名称文件

## 使用方法

基本用法：
```
python object_detection.py
```

命令行参数：
```
python object_detection.py --config yolov4-tiny.cfg --weights yolov4-tiny.weights --names coco.names.txt --camera 0 --confidence 0.5 --nms 0.4 --save --output output
```

参数说明：
- `--config`：YOLO配置文件路径（默认：yolov4-tiny.cfg）
- `--weights`：YOLO权重文件路径（默认：yolov4-tiny.weights）
- `--names`：类别名称文件路径（默认：coco.names.txt）
- `--camera`：摄像头索引（默认：0）
- `--confidence`：置信度阈值（默认：0.5）
- `--nms`：非极大值抑制阈值（默认：0.4）
- `--save`：启用检测结果保存功能
- `--output`：输出文件夹（默认：output）

## 键盘快捷键

在程序运行时，可以使用以下键盘快捷键：
- `q`：退出程序
- `s`：手动保存当前帧（如果启用了保存功能）

## 错误处理

应用程序包含多种错误处理机制：
- 检查所需文件是否存在
- 处理摄像头初始化失败的情况
- 处理视频帧获取失败时的重连机制
- 处理物体检测和渲染过程中的异常
- 防止非法的坐标值和数组访问错误

## 示例输出

程序在终端上会输出如下信息：
```
摄像头分辨率: 640x480, FPS: 30.0
已保存检测结果到: output/detection_20230915_153045.jpg
总运行时间: 120.56秒
处理帧数: 3512
平均FPS: 29.13
保存的检测结果: 15张
```

## 许可证

MIT 