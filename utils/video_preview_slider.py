import cv2
import random
from PySide6.QtWidgets import QLabel, QGraphicsOpacityEffect
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation
from PySide6.QtGui import QPixmap, QImage


class VideoPreview(QLabel):
    def __init__(self, video_path: str, parent=None):
        super().__init__(parent)
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet("background: black; border-radius: 10px;")
        self.cap = cv2.VideoCapture(video_path)
        self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))

        # эффект прозрачности
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)

        # таймер обновления
        self.timer = QTimer()
        self.timer.timeout.connect(self.fade_out)
        self.timer.start(5000)

        # анимации
        self.fade_out_anim = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_out_anim.setDuration(200)
        self.fade_out_anim.setStartValue(1)
        self.fade_out_anim.setEndValue(0)
        self.fade_out_anim.finished.connect(self.show_random_frame)

        self.fade_in_anim = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_in_anim.setDuration(500)
        self.fade_in_anim.setStartValue(0)
        self.fade_in_anim.setEndValue(1)

        # первый кадр сразу
        self.show_random_frame()

    def show_random_frame(self):
        if not self.cap.isOpened():
            return
        frame_num = random.randint(0, self.total_frames - 1)
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
        ret, frame = self.cap.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = frame.shape
            qimg = QImage(frame.data, w, h, ch * w, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(qimg).scaled(
                self.rect().width(), self.rect().height(),
                Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
            self.setPixmap(pixmap)
        # плавно показать новый кадр
        self.fade_in_anim.start()

    def fade_out(self):
        # сначала затемняем старый кадр
        self.fade_out_anim.start()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        # пересобрать текущий кадр при изменении размера
        self.show_random_frame()