import os
import subprocess
import sys

from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QWidget, QProgressBar, QGridLayout, QLabel, QPushButton

from classes.settings import Settings
# from classes.ui.context_menu import ContextMenu


class FileFrame:

    def __init__(self, app, index, file):
        self.app = app
        self.index = index

        self.frame = QWidget(app)
        self.frame.setObjectName('fileFrame')
        self.layout = QGridLayout(self.frame)
        self.frame.setLayout(self.layout)

        self.file_name = {'text': '', 'class': 'fileName'}
        self.size = {'text': '', 'class': 'fileSize'}
        self.slides = {'text': '', 'class': 'fileSlides'}
        self.status = {'text': 'В черзі', 'class': 'fileStatus'}
        self.progress = {'current': 0, 'total': 0}
        self.button = {'text': '', 'class': 'fileStatusFinished'}

        self.file_name['text'] = file.name
        self.file_name['widget'] = QLabel(self.file_name['text'])
        self.file_name['widget'].setObjectName(self.file_name['class'])

        self.size['text'] = f"Розмір файлу: {file.size} MB"
        self.size['widget'] = QLabel(self.size['text'])
        self.size['widget'].setObjectName(self.size['class'])

        self.slides['text'] = f"Слайдів: {file.slides}"
        self.slides['widget'] = QLabel(str(self.slides['text']))
        self.slides['widget'].setObjectName(self.slides['class'])

        self.status['text'] = self.status_to_text(file.status)
        self.status['widget'] = QLabel(self.status['text'])
        self.status['widget'].setObjectName(self.status['class'])

        self.progress['total'] = file.slides
        self.progress['widget'] = QProgressBar(app)
        self.progress['widget'].setMaximum(self.progress['total'])
        self.progress['widget'].setFormat('%v/%m')

        self.layout.addWidget(self.file_name['widget'], 0, 0, alignment=Qt.AlignmentFlag.AlignLeft)
        self.layout.addWidget(self.progress['widget'], 0, 1, 2, 1, alignment=Qt.AlignmentFlag.AlignVCenter)
        self.layout.addWidget(self.size['widget'], 1, 0, alignment=Qt.AlignmentFlag.AlignLeft)
        self.layout.addWidget(self.slides['widget'], 2, 0, alignment=Qt.AlignmentFlag.AlignLeft)
        self.layout.addWidget(self.status['widget'], 2, 1, alignment=Qt.AlignmentFlag.AlignCenter)

    def on_file_processing(self):
        self.status['text'] = self.status_to_text(1)
        self.update_status_label_widgets()

    def on_converting(self, current):
        self.progress['widget'].setValue(current)
        self.status['class'] = 'fileStatusConverting'
        self.status['text'] = self.status_to_text(2)
        self.update_status_label_widgets()

    def on_finished(self, time_spent, path):
        icon = QIcon(Settings.get_app_path() + '/assets/folder-open-regular.png')
        text = f"{self.status_to_text(3)} ({time_spent:.2f}с)"
        self.button['widget'] = QPushButton(icon, text)
        self.button['widget'].setObjectName('fileStatusFinished')
        self.button['widget'].clicked.connect(lambda: self.on_file_open_click(path))
        self.layout.addWidget(self.button['widget'], 2, 1, alignment=Qt.AlignmentFlag.AlignCenter)
        self.status['widget'].hide()

    def on_failed(self):
        self.status['text'] = self.status_to_text(4)
        self.status['class'] = "fileStatusFailed"
        self.update_status_label_widgets()

    @staticmethod
    def status_to_text(status):
        if status == 1:
            return 'Триває обробка файлу...'
        elif status == 2:
            return 'Конвертуємо слайди'
        elif status == 3:
            return 'Завершено'
        elif status == 4:
            return 'Виникла помилка =('
        else:
            return 'В черзі'

    def update_status_label_widgets(self):
        self.status['widget'].setText(self.status['text'])
        self.status['widget'].setObjectName(self.status['class'])
        self.status['widget'].style().unpolish(self.status['widget'])
        self.status['widget'].style().polish(self.status['widget'])

    @staticmethod
    def on_file_open_click(path):
        path = os.path.abspath(path)
        if sys.platform == 'darwin':  # macOS
            subprocess.Popen(['open', '--reveal', path])
        elif sys.platform in ("win32", "cygwin", "msys"):  # Windows
            subprocess.Popen(['explorer', '/select,', path])
