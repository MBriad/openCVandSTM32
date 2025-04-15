import cv2
import numpy as np
import os
import sys
import time
import argparse
from datetime import datetime

def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='YOLO物体检测应用')
    parser.add_argument('--config', default='yolov4-tiny.cfg', help='YOLO配置文件路径')
    parser.add_argument('--weights', default='yolov4-tiny.weights', help='YOLO权重文件路径')
    parser.add_argument('--names', default='coco.names.txt', help='类别名称文件路径')
    parser.add_argument('--camera', type=int, default=0, help='摄像头索引')
    parser.add_argument('--confidence', type=float, default=0.5, help='置信度阈值')
    parser.add_argument('--nms', type=float, default=0.4, help='非极大值抑制阈值')
    parser.add_argument('--save', action='store_true', help='保存检测结果')
    parser.add_argument('--output', default='output', help='输出文件夹')
    return parser.parse_args()

def check_files_exist(files):
    """检查所需文件是否存在"""
    for file_path in files:
        if not os.path.isfile(file_path):
            print(f"错误: 找不到文件 '{file_path}'")
            return False
    return True

def load_yolo_model(config_path, weights_path, names_path):
    """加载YOLO模型"""
    try:
        # 加载YOLO模型
        net = cv2.dnn.readNetFromDarknet(config_path, weights_path)
        
        # 获取输出层名称
        layer_names = net.getLayerNames()
        try:
            # OpenCV 4.5.4及更高版本
            output_layers = [layer_names[i-1] for i in net.getUnconnectedOutLayers()]
        except:
            # 旧版本OpenCV
            output_layers = [layer_names[i[0]-1] for i in net.getUnconnectedOutLayers()]
        
        # 加载类别名称
        try:
            with open(names_path, 'r') as f:
                classes = [line.strip() for line in f.readlines()]
        except Exception as e:
            print(f"错误: 无法读取类别文件: {e}")
            return None, None, None
        
        return net, output_layers, classes
    except Exception as e:
        print(f"错误: 无法加载YOLO模型: {e}")
        return None, None, None

def initialize_camera(camera_index):
    """初始化摄像头"""
    try:
        cap = cv2.VideoCapture(camera_index)
        if not cap.isOpened():
            print(f"错误: 无法打开摄像头 {camera_index}")
            return None
        return cap
    except Exception as e:
        print(f"错误: 初始化摄像头时出错: {e}")
        return None

def process_frame(frame, net, output_layers, classes, confidence_threshold, nms_threshold):
    """处理单帧图像并检测物体"""
    try:
        height, width, _ = frame.shape
        
        # 预处理图像
        blob = cv2.dnn.blobFromImage(frame, 1/255.0, (416, 416), swapRB=True, crop=False)
        net.setInput(blob)
        
        # 前向传播
        start_time = time.time()
        outs = net.forward(output_layers)
        end_time = time.time()
        inference_time = end_time - start_time
        
        # 处理检测结果
        class_ids = []
        confidences = []
        boxes = []
        
        for out in outs:
            for detection in out:
                scores = detection[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]
                
                if confidence > confidence_threshold:
                    # 物体位置
                    center_x = int(detection[0] * width)
                    center_y = int(detection[1] * height)
                    w = int(detection[2] * width)
                    h = int(detection[3] * height)
                    
                    # 矩形坐标
                    x = int(center_x - w / 2)
                    y = int(center_y - h / 2)
                    
                    boxes.append([x, y, w, h])
                    confidences.append(float(confidence))
                    class_ids.append(class_id)
        
        # 非极大值抑制
        indices = cv2.dnn.NMSBoxes(boxes, confidences, confidence_threshold, nms_threshold)
        
        detected_objects = []
        if len(indices) > 0:
            try:
                indices = indices.flatten()
            except:
                pass  # 版本兼容处理
                
            for i in indices:
                try:
                    i = i
                    x, y, w, h = boxes[i]
                    label = str(classes[class_ids[i]])
                    confidence = confidences[i]
                    detected_objects.append((x, y, w, h, label, confidence))
                except Exception as e:
                    print(f"警告: 处理检测结果时出错: {e}")
                    continue
        
        return detected_objects, inference_time
    except Exception as e:
        print(f"错误: 处理帧时出错: {e}")
        return [], 0

def draw_detections(frame, detections, colors):
    """在帧上绘制检测结果"""
    for x, y, w, h, label, confidence in detections:
        try:
            color = colors[hash(label) % len(colors)]
            
            # 确保坐标在图像范围内
            height, width, _ = frame.shape
            x = max(0, min(x, width-1))
            y = max(0, min(y, height-1))
            w = min(w, width-x)
            h = min(h, height-y)
            
            # 绘制边界框
            cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
            
            # 绘制标签
            text = f"{label} {confidence:.2f}"
            y1 = max(y - 10, 0)
            cv2.putText(frame, text, (x, y1), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        except Exception as e:
            print(f"警告: 绘制检测结果时出错: {e}")
            continue
    
    return frame

def save_detection_result(frame, output_dir):
    """保存检测结果"""
    try:
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        filename = os.path.join(output_dir, f"detection_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg")
        cv2.imwrite(filename, frame)
        print(f"已保存检测结果到: {filename}")
        return True
    except Exception as e:
        print(f"错误: 无法保存检测结果: {e}")
        return False

def main():
    """主函数"""
    # 解析命令行参数
    args = parse_arguments()
    
    # 检查文件是否存在
    required_files = [args.config, args.weights, args.names]
    if not check_files_exist(required_files):
        sys.exit(1)
    
    # 加载YOLO模型
    net, output_layers, classes = load_yolo_model(args.config, args.weights, args.names)
    if net is None or output_layers is None or classes is None:
        print("错误: 模型加载失败")
        sys.exit(1)
    
    # 设置随机颜色
    colors = np.random.uniform(0, 255, size=(100, 3))
    
    # 创建输出目录
    if args.save and not os.path.exists(args.output):
        try:
            os.makedirs(args.output)
        except Exception as e:
            print(f"错误: 无法创建输出目录: {e}")
            args.save = False
    
    # 初始化摄像头
    cap = initialize_camera(args.camera)
    if cap is None:
        sys.exit(1)
    
    # 获取视频流属性
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    print(f"摄像头分辨率: {frame_width}x{frame_height}, FPS: {fps}")
    
    # 创建窗口
    cv2.namedWindow("物体检测", cv2.WINDOW_NORMAL)
    
    frame_count = 0
    start_time = time.time()
    saved_count = 0
    
    try:
        while True:
            # 读取一帧
            ret, frame = cap.read()
            if not ret:
                print("警告: 无法获取视频帧，尝试重新连接...")
                # 尝试重新连接摄像头
                cap.release()
                cap = initialize_camera(args.camera)
                if cap is None:
                    break
                continue
            
            frame_count += 1
            
            # 处理帧
            detections, inference_time = process_frame(
                frame, net, output_layers, classes, 
                args.confidence, args.nms
            )
            
            # 绘制检测结果
            frame = draw_detections(frame, detections, colors)
            
            # 计算和显示FPS
            elapsed_time = time.time() - start_time
            if elapsed_time > 0:
                current_fps = frame_count / elapsed_time
                cv2.putText(frame, f"FPS: {current_fps:.1f}", (10, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            
            # 显示推理时间
            cv2.putText(frame, f"推理时间: {inference_time*1000:.1f}ms", (10, 60), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            
            # 显示检测到的物体数量
            cv2.putText(frame, f"检测到: {len(detections)}个物体", (10, 90), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            
            # 显示结果
            cv2.imshow("物体检测", frame)
            
            # 按键处理
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):  # 按'q'退出
                break
            elif key == ord('s') and args.save:  # 按's'保存当前帧
                save_detection_result(frame, args.output)
                saved_count += 1
            
            # 自动保存检测结果（如果启用）
            if args.save and len(detections) > 0 and frame_count % 30 == 0:
                save_detection_result(frame, args.output)
                saved_count += 1
    
    except KeyboardInterrupt:
        print("程序被用户中断")
    except Exception as e:
        print(f"错误: 程序异常: {e}")
    finally:
        # 释放资源
        if cap is not None:
            cap.release()
        cv2.destroyAllWindows()
        
        # 打印统计信息
        elapsed_time = time.time() - start_time
        if elapsed_time > 0 and frame_count > 0:
            print(f"总运行时间: {elapsed_time:.2f}秒")
            print(f"处理帧数: {frame_count}")
            print(f"平均FPS: {frame_count/elapsed_time:.2f}")
            if args.save:
                print(f"保存的检测结果: {saved_count}张")

if __name__ == "__main__":
    main() 