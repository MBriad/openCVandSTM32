import cv2
import numpy as np
import serial
import time
from camera import Camera

class ObjectDetector:
    def __init__(self, port='COM3', baudrate=115200):
        self.camera = Camera()
        self.serial = serial.Serial(port, baudrate, timeout=1)
        time.sleep(2)  # 等待串口初始化
        
    def detect_objects(self, frame):
        # 转换为灰度图
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # 高斯模糊
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        # 边缘检测
        edges = cv2.Canny(blurred, 50, 150)
        # 查找轮廓
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # 分析轮廓
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > 1000:  # 面积阈值
                # 获取轮廓的边界框
                x, y, w, h = cv2.boundingRect(contour)
                # 根据宽高比判断物体类型
                ratio = w / float(h)
                if 0.8 < ratio < 1.2:  # 近似正方形
                    return 'A'
                elif ratio > 1.5:  # 长方形
                    return 'B'
        return 'N'
    
    def send_command(self, command):
        try:
            self.serial.write(command.encode())
            response = self.serial.readline().decode().strip()
            print(f"发送命令: {command}, 收到响应: {response}")
        except Exception as e:
            print(f"串口通信错误: {e}")
    
    def run(self):
        try:
            while True:
                frame = self.camera.get_frame()
                if frame is None:
                    continue
                
                # 显示图像
                cv2.imshow('Object Detection', frame)
                
                # 检测物体并发送命令
                object_type = self.detect_objects(frame)
                self.send_command(object_type)
                
                # 按'q'退出
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                    
        finally:
            self.camera.release()
            cv2.destroyAllWindows()
            self.serial.close()

if __name__ == '__main__':
    detector = ObjectDetector()
    detector.run() 