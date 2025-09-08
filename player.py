import math
import sys
import random

from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtMultimediaWidgets import QGraphicsVideoItem
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QLineEdit, QWidget, QSizePolicy, \
    QPushButton, QGridLayout, QGraphicsScene, QGraphicsView, QSlider
from PySide6.QtCore import QTimer, Qt, QSize, QUrl
from PySide6.QtGui import QBrush, QColor, QPainter, QRadialGradient, QIcon, QPainterPath

class Blob:
    def __init__(self, x, y, radius):
        self.x = x
        self.y = y
        self.base_radius = radius
        self.phase = random.uniform(0, 2 * math.pi)  # для пульсации радиуса

        # Диапазоны RGB для голубо-синей гаммы
        self.r_min, self.r_max = 10, 120
        self.g_min, self.g_max = 10, 230
        self.b_min, self.b_max = 80, 255
        self.alpha_min, self.alpha_max = 80, 150

        # Фазы для синусоидального изменения цвета
        self.r_phase = random.uniform(0, 2 * math.pi)
        self.g_phase = random.uniform(0, 2 * math.pi)
        self.b_phase = random.uniform(0, 2 * math.pi)
        self.alpha_phase = random.uniform(0, 2 * math.pi)

        # текущий цвет
        self.color = self.calc_color(0)

    def radius(self, t):
        # Пульсация радиуса
        return self.base_radius + math.sin(t + self.phase) * 30

    def calc_color(self, t):
        # Плавное изменение RGB по синусам
        r = self.r_min + (self.r_max - self.r_min) * (0.5 + 0.5 * math.sin(self.r_phase + t / 2))
        g = self.g_min + (self.g_max - self.g_min) * (0.5 + 0.5 * math.sin(self.g_phase + t / 2))
        b = self.b_min + (self.b_max - self.b_min) * (0.5 + 0.5 * math.sin(self.b_phase + t / 2))
        a = self.alpha_min + (self.alpha_max - self.alpha_min) * (0.5 + 0.5 * math.sin(self.alpha_phase + t / 2))
        return QColor(int(r), int(g), int(b), int(a))

    def update_color(self, t):
        self.color = self.calc_color(t)


class MyWidget(QMainWindow):
    def __init__(self):
        super().__init__()

        # НАСТРОЙКИ ОКНА

        self.setWindowTitle("Сервис по просмотру аниме")
        self.w, self.h = 1000, 500
        self.resize(self.w, self.h)

        self.t = 0
        self.blobs = []
        self.main_color = QColor(255, 255, 255, 45)
        self.central = QWidget()


        # СЦЕНА И ПРОИГРЫВАНИЕ ВИДЕО

        self.scene = QGraphicsScene(self)
        self.view = QGraphicsView(self.scene, self.central)

        self.graphics_video_item = QGraphicsVideoItem()
        self.scene.addItem(self.graphics_video_item)

        self.player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.player.setAudioOutput(self.audio_output)
        self.player.setVideoOutput(self.graphics_video_item)

        video_path = "test_video.mp4"
        self.player.setSource(QUrl.fromLocalFile(video_path))
        self.player.durationChanged.connect(self.onDurationChanged)

        self.view.setRenderHint(QPainter.Antialiasing)
        self.view.setStyleSheet("background: transparent; border: none;")
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)


        # КНОПКИ УПРАВЛЕНИЯ ПРОИГРЫВАТЕЛЕМ

        self.controls_widget = QWidget(self.central)
        self.controls_widget.setAttribute(Qt.WA_TranslucentBackground)
        self.controls_layout = QGridLayout()
        self.controls_layout.setContentsMargins(20, 0, 20, 0)
        for i in range(5):
            self.controls_layout.setColumnStretch(i, 1)

        self.is_fullscreen = False
        self.is_playing = False  # изначально не играет

        # кнопка фулскрина
        self.fullscreen_btn = QPushButton(self.controls_widget)
        self.fullscreen_btn.setStyleSheet("background: transparent; border: none;")
        self.fullscreen_btn.setIconSize(QSize(40, 40))
        self.updateFullscreenIcon()
        self.fullscreen_btn.clicked.connect(self.makeFullscreen)

        # кнопка play/pause
        self.play_pause_btn = QPushButton(self.controls_widget)
        self.play_pause_btn.setFlat(True)
        self.play_pause_btn.setStyleSheet("background: transparent; border: none;")
        self.updatePlayPauseIcon()
        self.play_pause_btn.clicked.connect(self.togglePlayPause)

        # добавление кнопок в layout
        self.controls_layout.addWidget(self.play_pause_btn, 0, 2, alignment=Qt.AlignCenter)
        self.controls_layout.addWidget(self.fullscreen_btn, 0, 4, alignment=Qt.AlignRight)
        self.controls_widget.setLayout(self.controls_layout)

        # позиционирование панели кнопок
        rect_x, rect_y, rect_w, rect_h = self.getPlayerRect()
        controls_height = 50
        self.controls_widget.resize(rect_w, controls_height)
        self.controls_widget.move(0, rect_h - controls_height - 20)


        # ПОИСКОВАЯ СТРОКА

        self.search_layout = QVBoxLayout()
        self.search_layout.setContentsMargins(0, 20, 0, 0)
        self.search_layout.setSpacing(10)

        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Поиск аниме...")
        self.search_bar.setFixedHeight(40)
        self.search_bar.setStyleSheet("""
            QLineEdit {
                background-color: rgba(255, 255, 255, 45);
                border: 1px solid rgba(255, 255, 255, 80);
                border-radius: 10px;
                color: white;
                padding-left: 10px;
                font-size: 16px;
            }
        """)
        search_icon = QIcon("icons/loupe.png")
        self.search_bar.addAction(search_icon, QLineEdit.ActionPosition.TrailingPosition)
        self.search_bar.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        self.search_layout.addWidget(self.search_bar, alignment=Qt.AlignHCenter)
        self.search_layout.addStretch()

        self.central.setLayout(self.search_layout)
        self.setCentralWidget(self.central)


        # ТАЙМЛАЙН (слайдер позиции видео)

        self.timeline = QSlider(Qt.Horizontal, self.central)
        self.timeline_pos_is_fullscreen = lambda rect: [rect.x() + 10, rect.y() + rect.height() - 90, rect.width() - 20, 20]
        self.timeline_pos_is_small_screen = lambda rect: [rect[0] + 10, rect[1] + rect[3] - 80, rect[2] - 20, 20]


        # АНИМАЦИЯ (фоновый градиент)

        self.timer = QTimer()
        self.timer.timeout.connect(self.animate)
        self.timer.start(40)  # ~25fps


    # ТАЙМЛАЙН И ПОЗИЦИЯ ВИДЕО

    def onDurationChanged(self, duration_ms):
        self.timeline.setRange(0, duration_ms)
        self.timeline.sliderMoved.connect(self.onSeek)
        rect_x, rect_y, rect_w, rect_h = self.getPlayerRect()
        self.timeline.setGeometry(*self.timeline_pos_is_small_screen(self.getPlayerRect()))
        self.timeline.show()
        self.player.positionChanged.connect(lambda pos: self.timeline.setValue(pos))

    def onSeek(self, position_ms):
        self.player.setPosition(position_ms)


    # ОТРИСОВКА (фон, градиенты, плеер)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        self.drawBlobs(painter)
        self.drawPlayerBody(painter)

    def resizeEvent(self, event):
        self.generateBlobs()
        player_width = int(self.width() * 0.8)
        self.search_bar.setFixedWidth(player_width)

        if self.is_fullscreen:
            self._normal_rect = self.view.geometry()
            rect = self.central.rect()
            self.view.setGeometry(rect)
            self.timeline.setGeometry(*self.timeline_pos_is_fullscreen(rect))
            controls_height = 30
            self.controls_widget.resize(rect.width(), controls_height)
            self.controls_widget.move(rect.x(), rect.y() + rect.height() - controls_height - 20)
            self.graphics_video_item.setPos(0, 0)
            self.graphics_video_item.setSize(rect.size())
            self.view.setSceneRect(0, 0, rect.width(), rect.height())
            self.search_bar.hide()
        else:
            rect_x, rect_y, rect_w, rect_h = self.getPlayerRect()
            self.timeline.setGeometry(*self.timeline_pos_is_small_screen([rect_x, rect_y, rect_w, rect_h]))
            controls_height = 30
            self.controls_widget.resize(rect_w, controls_height)
            self.controls_widget.move(rect_x, rect_y + rect_h - controls_height - 20)
            self.view.setGeometry(rect_x, rect_y, rect_w, rect_h)
            self.graphics_video_item.setPos(0, 0)
            self.graphics_video_item.setSize(QSize(rect_w, rect_h))
            self.view.setSceneRect(0, 0, rect_w, rect_h)
            self.search_bar.show()
            path = QPainterPath()
            path.addRoundedRect(0, 0, rect_w, rect_h, 20, 20)

        self.update()
        super().resizeEvent(event)


    # ГРАДИЕНТНЫЕ ПЯТНА (фоновая анимация)

    def generateBlobs(self):
        self.blobs = []
        for _ in range(18):
            x = random.randint(-100, self.width() + 100)
            y = random.randint(-100, self.height() + 100)
            radius = random.randint(int(self.height() * 0.3), int(self.width() * 0.55))
            self.blobs.append(Blob(x, y, radius))

    def animate(self):
        self.t += 0.03
        for blob in self.blobs:
            blob.update_color(self.t)
        self.update()

    def drawBlobs(self, painter):
        painter.fillRect(self.rect(), QColor(10, 20, 40))
        for blob in self.blobs:
            grad = QRadialGradient(blob.x, blob.y, blob.radius(self.t))
            grad.setColorAt(0, blob.color.lighter(160))
            grad.setColorAt(1, QColor(0, 0, 0, 0))
            painter.setBrush(QBrush(grad))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(
                blob.x - blob.radius(self.t),
                blob.y - blob.radius(self.t),
                blob.radius(self.t) * 2,
                blob.radius(self.t) * 2
            )


    # ПЛЕЕР: размеры, отрисовка, кнопки

    def getPlayerRect(self):
        w = int(self.width() * 0.8)
        h = int(self.height() * 0.65)
        x = (self.width() - w) // 2
        y = (self.height() - h) // 2
        return x, y, w, h

    def drawPlayerBody(self, painter):
        x, y, w, h = self.getPlayerRect()
        painter.setBrush(self.main_color)
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(x, y, w, h, 20, 20)

    def updatePlayPauseIcon(self):
        icon = QIcon("icons/pause.png") if self.is_playing else QIcon("icons/play.png")
        self.play_pause_btn.setIcon(icon)
        self.play_pause_btn.setIconSize(QSize(40, 40))

    def togglePlayPause(self):
        self.is_playing = not self.is_playing
        self.updatePlayPauseIcon()
        if self.is_playing:
            self.player.play()
        else:
            self.player.pause()

    def updateFullscreenIcon(self):
        icon = QIcon("icons/minimize.png") if self.is_fullscreen else QIcon("icons/fullscreen.png")
        self.fullscreen_btn.setIcon(icon)
        self.fullscreen_btn.setIconSize(QSize(40, 40))

    def makeFullscreen(self):
        self.is_fullscreen = not self.is_fullscreen
        self.updateFullscreenIcon()

        if self.is_fullscreen:
            self.central.setStyleSheet('background: #000;')
            self._normal_rect = self.view.geometry()
            rect = self.central.rect()
            self.view.setGeometry(rect)
            self.timeline.setGeometry(*self.timeline_pos_is_fullscreen(rect))
            controls_height = 30
            self.controls_widget.resize(rect.width(), controls_height)
            self.controls_widget.move(rect.x(), rect.y() + rect.height() - controls_height - 20)
            self.graphics_video_item.setPos(0, 0)
            self.graphics_video_item.setSize(rect.size())
            self.view.setSceneRect(0, 0, rect.width(), rect.height())
            self.search_bar.hide()
        else:
            self.central.setStyleSheet('background: transparent;')
            rect_x, rect_y, rect_w, rect_h = self.getPlayerRect()
            self.timeline.setGeometry(*self.timeline_pos_is_small_screen([rect_x, rect_y, rect_w, rect_h]))
            controls_height = 30
            self.controls_widget.resize(rect_w, controls_height)
            self.controls_widget.move(rect_x, rect_y + rect_h - controls_height - 20)
            self.view.setGeometry(rect_x, rect_y, rect_w, rect_h)
            self.graphics_video_item.setPos(0, 0)
            self.graphics_video_item.setSize(QSize(rect_w, rect_h))
            self.view.setSceneRect(0, 0, rect_w, rect_h)
            self.search_bar.show()
            path = QPainterPath()
            path.addRoundedRect(0, 0, rect_w, rect_h, 20, 20)



def start() -> None:
    app = QApplication(sys.argv)

    widget = MyWidget()
    widget.resize(800, 600)
    widget.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    start()