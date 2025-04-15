import cv2

class Camera:
    def __init__(self, camera_id=0):
        self.camera = cv2.VideoCapture(camera_id)
        if not self.camera.isOpened():
            raise RuntimeError("无法打开摄像头")
        
        # 设置相机分辨率
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
    def get_frame(self):
        ret, frame = self.camera.read()
        if not ret:
            print("无法获取图像帧")
            return None
        return frame
    
    def release(self):
        self.camera.release() 