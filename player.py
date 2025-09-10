import math
import sys
import random
import datetime

from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtMultimediaWidgets import QGraphicsVideoItem
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QLineEdit, QWidget, QSizePolicy, \
    QPushButton, QGridLayout, QGraphicsScene, QGraphicsView, QSlider, QLabel
from PySide6.QtCore import QTimer, Qt, QSize, QUrl
from PySide6.QtGui import QBrush, QColor, QPainter, QRadialGradient, QIcon, QPainterPath, QKeySequence

from utils.preview_thumbnail import TimelinePreview
from utils.video_preview_slider import VideoPreview


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

        # Центральный виджет

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
        self.view.setStyleSheet("background: black; border: none;")
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.path = QPainterPath()

        # СЛАЙДЕР ПРЕВЬЮ

        self.preview_slider = VideoPreview(video_path, self.central)

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

        # кнопка начала видео
        self.start_video = QPushButton(self.central, self.preview_slider)
        self.start_video.setIcon(QIcon('icons/play_bigger.png'))
        self.start_video.setIconSize(QSize(60, 60))
        self.start_video.setFixedSize(100, 100)
        self.start_video.setStyleSheet("background: transparent; border: none;")
        self.start_video.clicked.connect(self.togglePlayPause)


        # добавление кнопок в layout
        self.controls_layout.addWidget(self.play_pause_btn, 0, 2, alignment=Qt.AlignCenter)
        self.controls_layout.addWidget(self.fullscreen_btn, 0, 4, alignment=Qt.AlignRight)
        self.controls_widget.setLayout(self.controls_layout)

        self.controls_widget.hide()


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
        self.timeline.setStyleSheet("""
            QSlider::groove:horizontal {
                height: 6px;
                background: #e0e0e0;
                border-radius: 3px;
            }

            QSlider::sub-page:horizontal {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #4facfe, stop:1 #00f2fe
                );
                border-radius: 3px;
            }

            QSlider::add-page:horizontal {
                background: #e0e0e0;
                border-radius: 3px;
            }

            QSlider::handle:horizontal {
                background: white;
                border: 2px solid #4facfe;
                width: 14px;
                height: 14px;
                margin: -5px 0;
                border-radius: 7px;
            }

            QSlider::handle:horizontal:hover {
                background: #f0faff;
                border: 2px solid #00f2fe;
            }

            QSlider::handle:horizontal:pressed {
                background: #e6f7ff;
                border: 2px solid #0099ff;
            }
        """)

        self.timeline_preview = TimelinePreview(video_path, self.central)

        # показываем кадры при движении ползунка
        self.timeline.sliderPressed.connect(self.onSliderPressed)
        self.timeline.sliderMoved.connect(self.onTimelineHover)
        self.timeline.sliderReleased.connect(self.onSliderReleased)

        self.timeline_pos_is_fullscreen = lambda rect: [rect.x() + 10, rect.y() + rect.height() - 90, rect.width() - 20, 20]
        self.timeline_pos_is_small_screen = lambda rect: [rect[0] + 10, rect[1] + rect[3] - 80, rect[2] - 20, 20]


        # TIMELINE ВРЕМЕННОЙ СЧЕТЧИК

        self.video_duration_timer = QLabel(self.controls_widget)
        self.controls_layout.addWidget(self.video_duration_timer, 0, 0, alignment=Qt.AlignLeft)


        # АНИМАЦИЯ (фоновый градиент)

        self.timer = QTimer()
        self.timer.timeout.connect(self.animate)
        self.timer.timeout.connect(self.hide_player_controls)
        self.timer.start(40)  # ~25fps

        # Убираем фокус с виджетов

        self.play_pause_btn.setFocusPolicy(Qt.NoFocus)
        self.fullscreen_btn.setFocusPolicy(Qt.NoFocus)
        self.start_video.setFocusPolicy(Qt.NoFocus)
        self.search_bar.setFocusPolicy(Qt.ClickFocus)


    # ТАЙМЛАЙН И ПОЗИЦИЯ ВИДЕО

    def format_timedelta(self, td: datetime.timedelta) -> str:
        total_seconds = int(td.total_seconds())

        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)

        if hours > 0:
            return f"{hours:02}:{minutes:02}:{seconds:02}"
        else:
            return f"{minutes:02}:{seconds:02}"

    def onSliderPressed(self):
        # ставим видео на паузу
        self.was_playing = self.is_playing
        self.player.pause()
        self.is_playing = False

    def onTimelineHover(self, position_ms):
        self.mouseMovedInsidePlayer()
        self.timeline_preview.show_frame_at(position_ms)

        slider_geom = self.timeline.geometry()
        preview_w = self.timeline_preview.width()
        x = slider_geom.x() + int(slider_geom.width() * (position_ms / self.timeline.maximum())) - preview_w // 2
        y = slider_geom.y() - self.timeline_preview.height() - 10

        self.timeline_preview.move(x, y)
        self.timeline_preview.show()

    def onSliderReleased(self):
        # когда отпустили слайдер — реально перемещаем плеер
        position_ms = self.timeline.value()
        self.player.setPosition(position_ms)
        self.timeline_preview.hide()

        # если до этого играло — продолжаем
        if self.was_playing:
            self.player.play()
            self.is_playing = True

    def keyPressEvent(self, event, /):
        key = event.key()
        native = event.nativeVirtualKey()

        if key == Qt.Key_Space:
            self.togglePlayPause()
            self.mouseMovedInsidePlayer()
        elif native == 0x46:
            self.makeFullscreen()
        elif key == Qt.Key_Escape:
            self.is_fullscreen = True
            self.makeFullscreen()


    def onDurationChanged(self, duration_ms):
        if len(self.video_duration_timer.text()) == 0:
            self.view.setMouseTracking(False)
            self.preview_slider.show()

        self.timeline.setRange(0, duration_ms)
        self.timeline.setGeometry(*self.timeline_pos_is_small_screen(self.getPlayerRect()))

        self.player.positionChanged.connect(self.onVideoMovement)
        self.video_duration_timer.setText(self.format_timedelta(datetime.timedelta(milliseconds=self.player.duration())))
        self.timeline.hide()


    def onVideoMovement(self, pos):
        self.timeline.setValue(pos)

        video_duration = self.format_timedelta(datetime.timedelta(milliseconds=pos))
        video_total_duration = self.format_timedelta(datetime.timedelta(milliseconds=self.player.duration()))
        video_duration_and_timer = f'{video_duration}/{video_total_duration}'
        self.video_duration_timer.setText(video_duration_and_timer)


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
        self.timeline.hide()

        controls_height = 30
        rect_x, rect_y, rect_w, rect_h = self.getPlayerRect()
        self.view.setGeometry(rect_x, rect_y, rect_w, rect_h)
        self.graphics_video_item.setSize(QSize(rect_w, rect_h))

        btn_w, btn_h = self.start_video.width(), self.start_video.height()
        self.start_video.move(
            rect_x + rect_w // 2 - btn_w // 2,
            rect_y + rect_h // 2 - btn_h // 2
        )

        self.view.mousePressEvent = self.togglePlayPause

        if self.is_fullscreen:
            rect = self.central.rect()
            self.view.setGeometry(rect)
            self.timeline.setGeometry(*self.timeline_pos_is_fullscreen(rect))
            self.controls_widget.resize(rect.width(), controls_height)
            self.controls_widget.move(rect.x(), rect.y() + rect.height() - controls_height - 20)
            self.graphics_video_item.setPos(0, 0)
            self.graphics_video_item.setSize(rect.size())
            self.view.setSceneRect(0, 0, rect.width(), rect.height())

            self.preview_slider.setGeometry(rect.x(), rect.y(), rect.size().width(), rect.size().height())

            self.search_bar.hide()
            self.view.clearMask()
        else:
            self.timeline.setGeometry(*self.timeline_pos_is_small_screen([rect_x, rect_y, rect_w, rect_h]))
            self.controls_widget.resize(rect_w, controls_height)
            self.controls_widget.move(rect_x, rect_y + rect_h - controls_height - 20)
            self.view.setGeometry(rect_x, rect_y, rect_w, rect_h)
            self.graphics_video_item.setPos(0, 0)
            self.graphics_video_item.setSize(QSize(rect_w, rect_h))
            self.view.setSceneRect(0, 0, rect_w, rect_h)

            self.preview_slider.setGeometry(rect_x, rect_y, rect_w, rect_h)

            self.search_bar.show()
            path = QPainterPath()
            path.addRoundedRect(0, 0, rect_w, rect_h, 20, 20)
            self.view.setMask(path.toFillPolygon().toPolygon())

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

    def togglePlayPause(self, event=None):
        self.view.setMouseTracking(True)
        self.view.mouseMoveEvent = self.mouseMovedInsidePlayer
        self.is_playing = not self.is_playing
        self.updatePlayPauseIcon()
        if self.is_playing:
            self.player.play()
            self.start_video.hide()
            self.preview_slider.hide()
        else:
            self.player.pause()
            self.start_video.show()

    def updateFullscreenIcon(self):
        icon = QIcon("icons/minimize.png") if self.is_fullscreen else QIcon("icons/fullscreen.png")
        self.fullscreen_btn.setIcon(icon)
        self.fullscreen_btn.setIconSize(QSize(40, 40))

    def makeFullscreen(self):
        self.is_fullscreen = not self.is_fullscreen
        self.updateFullscreenIcon()

        if self.is_fullscreen:
            self.central.setStyleSheet('background: #000;')
            rect = self.central.rect()
            self.view.setGeometry(rect)
            self.timeline.setGeometry(*self.timeline_pos_is_fullscreen(rect))
            controls_height = 30
            self.controls_widget.resize(rect.width(), controls_height)
            self.controls_widget.move(rect.x(), rect.y() + rect.height() - controls_height - 20)
            self.graphics_video_item.setPos(0, 0)
            self.graphics_video_item.setSize(rect.size())
            self.view.setSceneRect(0, 0, rect.width(), rect.height())

            self.preview_slider.setGeometry(rect.x(), rect.y(), rect.size().width(), rect.size().height())

            self.search_bar.hide()
            self.view.clearMask()
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

            self.preview_slider.setGeometry(rect_x, rect_y, rect_w, rect_h)

            self.search_bar.show()
            path = QPainterPath()
            path.addRoundedRect(0, 0, rect_w, rect_h, 20, 20)
            self.view.setMask(path.toFillPolygon().toPolygon())


    def mouseMovedInsidePlayer(self, event=None):
        self.timeline.show()
        self.controls_widget.show()
        self.timer.start(4000)

    def hide_player_controls(self):
        self.timeline.hide()
        self.controls_widget.hide()


# Кнопки промотки, при использовании слайдера показывать кадр


def start() -> None:
    app = QApplication(sys.argv)

    widget = MyWidget()
    widget.resize(800, 600)
    widget.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    start()