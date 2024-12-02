import cv2

class VideoCapture:
    def __init__(self, camera_index=0):
        self.camera_index = camera_index
        self.capture = cv2.VideoCapture(self.camera_index)
        if not self.capture.isOpened():
            raise ValueError(f"Cannot open camera with index {camera_index}")

    def get_frame(self):
        ret, frame = self.capture.read()
        if not ret:
            raise RuntimeError("Failed to capture frame from camera")
        return frame

    def release(self):
        self.capture.release()
