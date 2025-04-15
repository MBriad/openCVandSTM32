import cv2
import numpy as np
import os
import time
import serial
import argparse

def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='YOLO物体检测与串口通信')
    parser.add_argument('--config', default='yolov4-tiny.cfg', help='YOLO配置文件路径')
    parser.add_argument('--weights', default='yolov4-tiny.weights', help='YOLO权重文件路径')
    parser.add_argument('--names', default='coco.names.txt', help='类别名称文件路径')
    parser.add_argument('--camera', type=int, default=0, help='摄像头索引')
    parser.add_argument('--confidence', type=float, default=0.5, help='置信度阈值')
    parser.add_argument('--port', default='COM3', help='串口端口')
    parser.add_argument('--baud', type=int, default=9600, help='波特率')
    parser.add_argument('--objectA', default='person', help='要检测的物体A')
    parser.add_argument('--objectB', default='car', help='要检测的物体B')
    return parser.parse_args()

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

def initialize_serial(port, baud_rate):
    """初始化串口通信"""
    try:
        ser = serial.Serial(port, baud_rate, timeout=1)
        if ser.isOpen():
            print(f"串口 {port} 已打开，波特率: {baud_rate}")
            return ser
        else:
            print(f"错误: 无法打开串口 {port}")
            return None
    except Exception as e:
        print(f"错误: 初始化串口时出错: {e}")
        return None

def process_frame(frame, net, output_layers, classes, confidence_threshold):
    """处理单帧图像并检测物体"""
    try:
        height, width, _ = frame.shape
        
        # 预处理图像
        blob = cv2.dnn.blobFromImage(frame, 1/255.0, (416, 416), swapRB=True, crop=False)
        net.setInput(blob)
        
        # 前向传播
        outs = net.forward(output_layers)
        
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
        indices = cv2.dnn.NMSBoxes(boxes, confidences, confidence_threshold, 0.4)
        
        detected_objects = []
        if len(indices) > 0:
            try:
                indices = indices.flatten()
            except:
                pass  # 版本兼容处理
                
            for i in indices:
                try:
                    i = i
                    label = str(classes[class_ids[i]])
                    confidence = confidences[i]
                    detected_objects.append(label)
                except Exception as e:
                    print(f"警告: 处理检测结果时出错: {e}")
                    continue
        
        return detected_objects
    except Exception as e:
        print(f"错误: 处理帧时出错: {e}")
        return []

def main():
    # 解析命令行参数
    args = parse_arguments()
    
    # 加载YOLO模型
    net, output_layers, classes = load_yolo_model(args.config, args.weights, args.names)
    if net is None or output_layers is None or classes is None:
        print("错误: 模型加载失败")
        return
    
    # 初始化摄像头
    cap = initialize_camera(args.camera)
    if cap is None:
        return
    
    # 初始化串口
    ser = initialize_serial(args.port, args.baud)
    if ser is None:
        cap.release()
        return
    
    # 创建窗口
    cv2.namedWindow("物体检测与串口通信", cv2.WINDOW_NORMAL)
    
    last_sent = 'N'  # 上一次发送的状态，初始为'N'
    
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
            
            # 处理帧并检测物体
            detected_objects = process_frame(
                frame, net, output_layers, classes, args.confidence
            )
            
            # 根据检测结果发送串口信息
            to_send = 'N'  # 默认发送'N'表示未检测到指定物体
            
            # 检查是否检测到物体A
            if args.objectA in detected_objects:
                to_send = 'A'
            # 如果已经检测到物体A，就不再检查物体B
            elif args.objectB in detected_objects:
                to_send = 'B'
            
            # 只有当检测状态变化时才发送
            if to_send != last_sent:
                try:
                    ser.write(to_send.encode())
                    last_sent = to_send
                    print(f"已发送: {to_send}")
                except Exception as e:
                    print(f"错误: 发送串口数据时出错: {e}")
            
            # 在帧上显示当前状态
            status_text = f"已检测到: {', '.join(detected_objects)}" if detected_objects else "未检测到目标物体"
            send_text = f"发送状态: {to_send}"
            
            cv2.putText(frame, status_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(frame, send_text, (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            # 显示帧
            cv2.imshow("物体检测与串口通信", frame)
            
            # 按ESC键退出
            if cv2.waitKey(1) == 27:
                break
    
    except KeyboardInterrupt:
        print("程序被用户中断")
    finally:
        # 释放资源
        if ser and ser.isOpen():
            ser.close()
            print("串口已关闭")
        cap.release()
        cv2.destroyAllWindows()
        print("程序已退出")

if __name__ == "__main__":
    main()
