import cv2

from PySide6.QtCore import Qt
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import QLabel


class TimelinePreview(QLabel):
    def __init__(self, video_path: str, parent=None):
        super().__init__(parent)
        self.setFixedSize(160, 90)
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet("background: black; border: 2px solid white; border-radius: 6px;")
        self.hide()

        self.cache = []

        self.build_cache(video_path, step_sec=3)

    def build_cache(self, video_path: str, step_sec: int = 5):
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            return

        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = total_frames / fps * 1000  # в мс

        step_ms = step_sec * 1000
        t = 0
        while t < duration:
            cap.set(cv2.CAP_PROP_POS_MSEC, t)
            ret, frame = cap.read()
            if not ret:
                break
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = frame.shape
            qimg = QImage(frame.data, w, h, ch * w, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(qimg).scaled(
                self.width(), self.height(),
                Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
            self.cache.append((t, pixmap))
            t += step_ms

        cap.release()

    def show_frame_at(self, position_ms: int):
        if not self.cache:
            return


        closest = min(self.cache, key=lambda x: abs(x[0] - position_ms))
        self.setPixmap(closest[1])
