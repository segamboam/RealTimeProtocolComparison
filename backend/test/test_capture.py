from backend.video.capture import VideoCapture
import cv2

if __name__ == "__main__":
    video = VideoCapture()
    try:
        while True:
            frame = video.get_frame()
            cv2.imshow("Camera Feed", frame)

            # Presiona 'q' para salir
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    finally:
        video.release()
        cv2.destroyAllWindows()
