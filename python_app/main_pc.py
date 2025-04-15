import cv2

def main():
    # 初始化摄像头，使用默认摄像头（通常为0）
    cap = cv2.VideoCapture(0)
    
    # 检查摄像头是否成功打开
    if not cap.isOpened():
        print("error: cannot open camera")
        return
    
    # 创建一个窗口用于显示视频
    cv2.namedWindow("video", cv2.WINDOW_NORMAL)
    
    while True:
        # 读取一帧视频
        ret, frame = cap.read()
        
        # 检查是否成功读取帧
        if not ret:
            print("error: cannot get video frame")
            break
        
        # 显示视频帧
        cv2.imshow("video", frame)
        
        # 按下'q'键退出循环
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    # 释放资源
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
