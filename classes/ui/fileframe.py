import os
import subprocess
import sys

from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon, QFontMetrics
from PySide6.QtWidgets import QWidget, QProgressBar, QGridLayout, QHBoxLayout, QLabel, QToolButton
from pytablericons import TablerIcons, OutlineIcon


class FileFrame:

    FORMAT_ICON = {
        'pptx': OutlineIcon.PRESENTATION,
        'png': OutlineIcon.PHOTO,
    }

    def __init__(self, app, index, file):
        self.app = app
        self.index = index
        self.path = None
        self.file = file

        self.frame = QWidget(app)
        self.frame.setObjectName('fileFrame')
        self.outer_layout = QHBoxLayout(self.frame)
        self.outer_layout.setContentsMargins(0, 0, 0, 0)
        self.outer_layout.setSpacing(0)
        self.layout = QGridLayout()
        self.layout.setContentsMargins(8, 8, 8, 8)
        self.layout.setHorizontalSpacing(10)
        self.frame.setLayout(self.outer_layout)

        self.badge = {'text': '', 'class': 'fileBadge'}
        self.file_name = {'text': '', 'class': 'fileName'}
        self.size = {'text': '', 'class': 'fileSize'}
        self.status = {'text': 'В черзі', 'class': 'fileStatus'}
        self.progress = {'current': 0, 'total': 0, 'class': 'fileProgress'}
        self.button = {'text': '', 'class': 'fileAction'}
        self.cancel_button = {'text': '', 'class': 'fileCancelAction'}

        self.badge['widget'] = QLabel(self.frame)
        self.badge['icon'] = self.FORMAT_ICON.get(self.file.target_format, OutlineIcon.PRESENTATION)
        self.badge['widget'].setPixmap(self._tabler_icon(self.badge['icon'], 'GRAY', 18).pixmap(18, 18))
        self.badge['widget'].setObjectName(self.badge['class'])
        self.badge['widget'].setFixedSize(34, 58)
        self.badge['widget'].setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.metadata_row = QHBoxLayout()
        self.metadata_row.setSpacing(8)

        self.file_name['text'] = file.name
        self.file_name['widget'] = QLabel(self.file_name['text'])
        elided = QFontMetrics(self.file_name['widget'].font()).elidedText(file.name, Qt.TextElideMode.ElideMiddle, 260)
        self.file_name['widget'].setText(elided)
        self.file_name['widget'].setToolTip(file.name)
        self.file_name['widget'].setObjectName(self.file_name['class'])

        self.size['text'] = f"{file.size} MB → {self.file.target_format.upper()}"
        self.size['widget'] = QLabel(self.size['text'])
        self.size['widget'].setObjectName(self.size['class'])

        self.status['text'] = self.status_to_text(file.status)
        self.status['widget'] = QLabel(self.status['text'], alignment=Qt.AlignmentFlag.AlignBottom)
        self.status['widget'].setObjectName(self.status['class'])
        self.status['widget'].setFixedHeight(16)

        self.progress['total'] = file.slides
        self.progress['widget'] = QProgressBar(app)
        self.progress['widget'].setMaximum(self.progress['total'])
        self.progress['widget'].setTextVisible(False)
        self.progress['widget'].setFixedHeight(3)

        self.button['widget'] = QToolButton(self.frame)
        self.button['widget'].setIcon(self._tabler_icon(OutlineIcon.FOLDER, '#8a8a8e', 16))
        self.button['widget'].setObjectName(self.button['class'])
        self.button['widget'].setAutoRaise(True)
        self.button['widget'].setIconSize(QSize(16, 16))
        self.button['widget'].setFixedSize(28, 28)
        self.button['widget'].clicked.connect(self.on_file_open_click)

        self.cancel_button['widget'] = QToolButton(self.frame)
        self.cancel_button['widget'].setIcon(self._tabler_icon(OutlineIcon.BAN, '#8a8a8e', 16))
        self.cancel_button['widget'].setObjectName(self.cancel_button['class'])
        self.cancel_button['widget'].setAutoRaise(True)
        self.cancel_button['widget'].setIconSize(QSize(16, 16))
        self.cancel_button['widget'].setFixedSize(28, 28)
        self.cancel_button['widget'].clicked.connect(self.cancel_conversion)

        self.outer_layout.addWidget(self.badge['widget'], alignment=Qt.AlignmentFlag.AlignLeft)
        self.outer_layout.addLayout(self.layout)
        self.layout.addWidget(self.file_name['widget'], 0, 0, alignment=Qt.AlignmentFlag.AlignLeft)
        self.layout.addWidget(self.progress['widget'], 2, 0, alignment=Qt.AlignmentFlag.AlignVCenter)
        self.layout.addLayout(self.metadata_row, 1, 0)
        self.metadata_row.addWidget(self.size['widget'], stretch=1)
        self.metadata_row.addWidget(self.status['widget'], alignment=Qt.AlignmentFlag.AlignRight)
        self.layout.addWidget(self.button['widget'], 0, 1, 3, 1, alignment=Qt.AlignmentFlag.AlignRight)
        self.layout.addWidget(self.cancel_button['widget'], 0, 1, 3, 1, alignment=Qt.AlignmentFlag.AlignRight)
        self.button['widget'].hide()

    def on_file_processing(self):
        self.file.status = 1
        self.badge['class'] = 'fileBadgeProcessing'
        self.badge['icon'] = self.FORMAT_ICON.get(self.file.target_format, OutlineIcon.PRESENTATION)
        self.badge['widget'].setPixmap(self._tabler_icon(self.badge['icon'], '#378add', 18).pixmap(18, 18))
        self.progress['class'] = 'fileProgressProcessing'
        self.status['class'] = 'fileStatusProcessing'
        self.status['text'] = f"{self.status_to_text(self.file.status)} · {self.progress['total']} слайдів"
        self.frame.setObjectName('fileFrameProcessing')
        self.update_widgets_styles()

    def on_converting(self, current):
        self.file.status = 2
        self.badge['class'] = 'fileBadgeConverting'
        self.badge['icon'] = self.FORMAT_ICON.get(self.file.target_format, OutlineIcon.PRESENTATION)
        self.badge['widget'].setPixmap(self._tabler_icon(self.badge['icon'], '#378add', 18).pixmap(18, 18))
        self.progress['class'] = 'fileProgressConverting'
        self.progress['current'] = current
        self.progress['widget'].setValue(self.progress['current'])
        self.status['class'] = 'fileStatusConverting'
        self.status['text'] = f"{self.status_to_text(self.file.status)} · {self.progress['current']}/{self.progress['total']}"
        self.frame.setObjectName('fileFrameConverting')
        self.update_widgets_styles()

    def on_finished(self, time_spent, path):
        self.file.status = 3
        self.path = path
        self.badge['class'] = 'fileBadgeFinished'
        self.badge['icon'] = self.FORMAT_ICON.get(self.file.target_format, OutlineIcon.PRESENTATION)
        self.badge['widget'].setPixmap(self._tabler_icon(self.badge['icon'], '#639922', 18).pixmap(18, 18))
        self.progress['class'] = 'fileProgressFinished'
        self.status['class'] = 'fileStatusFinished'
        self.status['text'] = f"{self.status_to_text(self.file.status)} · {self.progress['current']}/{self.progress['total']}"
        self.frame.setObjectName('fileFrameFinished')
        self.cancel_button['widget'].hide()
        self.button['widget'].show()
        self.update_widgets_styles()

    def on_failed(self):
        self.file.status = 4
        self.badge['class'] = 'fileBadgeFailed'
        self.badge['icon'] = self.FORMAT_ICON.get(self.file.target_format, OutlineIcon.PRESENTATION)
        self.badge['widget'].setPixmap(self._tabler_icon(self.badge['icon'], '#e24b4a', 18).pixmap(18, 18))
        self.progress['class'] = 'fileProgressFailed'
        self.status['text'] = f"{self.status_to_text(self.file.status)} · {self.progress['current']}/{self.progress['total']}"
        self.status['class'] = "fileStatusFailed"
        self.frame.setObjectName('fileFrameFailed')
        self.update_widgets_styles()

    def on_canceled(self):
        self.file.status = 5
        self.status['text'] = f"{self.status_to_text(self.file.status)} · {self.progress['current']}/{self.progress['total']}"
        self.badge['class'] = 'fileBadgeCanceled'
        self.badge['icon'] = self.FORMAT_ICON.get(self.file.target_format, OutlineIcon.PRESENTATION)
        self.badge['widget'].setPixmap(self._tabler_icon(self.badge['icon'], '#8a8a8e', 18).pixmap(18, 18))
        self.status['class'] = "fileStatusCanceled"
        self.progress['class'] = 'fileProgressCanceled'
        self.frame.setObjectName('fileFrameCanceled')
        self.update_widgets_styles()

    @staticmethod
    def status_to_text(status):
        return {
            0: '⋯ В черзі',
            1: '⇢ Триває обробка файлу...',
            2: '↻ Конвертуємо слайди',
            3: '🗸 Завершено',
            4: '⚠ Виникла помилка',
            5: '✖ Конвертація скасована'
        }.get(status, '⋯ В черзі')

    def update_widgets_styles(self):
        self.status['widget'].setText(self.status['text'])
        self.status['widget'].setObjectName(self.status['class'])
        self.status['widget'].style().unpolish(self.status['widget'])
        self.status['widget'].style().polish(self.status['widget'])

        self.progress['widget'].setObjectName(self.progress['class'])
        self.progress['widget'].style().unpolish(self.progress['widget'])
        self.progress['widget'].style().polish(self.progress['widget'])

        self.badge['widget'].setObjectName(self.badge['class'])
        self.badge['widget'].style().unpolish(self.badge['widget'])
        self.badge['widget'].style().polish(self.badge['widget'])

        self.frame.style().unpolish(self.frame)
        self.frame.style().polish(self.frame)

    def on_file_open_click(self):
        path = os.path.abspath(self.path)
        if sys.platform == 'darwin':  # macOS
            subprocess.Popen(['open', '--reveal', path])
        elif sys.platform in ("win32", "cygwin", "msys"):  # Windows
            subprocess.Popen(['explorer', '/select,', path])

    def cancel_conversion(self):
        self.app.cancel_conversion.emit(self.index)

    @staticmethod
    def _tabler_icon(name: OutlineIcon, color: str, size: int = 18) -> QIcon:
        """Cached so the same (icon, color) pair is only rasterized once."""
        img = TablerIcons.load(name, size=size, color=color, stroke_width=2.0)
        return QIcon(img.toqpixmap())
