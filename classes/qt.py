import os
import sys
import subprocess

from PySide6 import QtWidgets
from PySide6.QtWidgets import (QFileDialog, QWidget, QLabel, QProgressBar, QGridLayout,
                               QVBoxLayout, QScrollArea, QMainWindow, QPushButton)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (QFileDialog, QWidget, QLabel, QProgressBar, QGridLayout, QMessageBox,

from classes.threads.request_password import RequestPasswordThread
from classes.threads.worker import WorkerThread
from classes.validator import Validator
from classes.settings import Settings
from classes.ui.menu import MenuUI
from classes.pdf_file import File


class QtApp(QMainWindow):

    encrypted_file_added = Signal(File)
    terminate_password_thread = Signal()
    file_added = Signal(list)

    def __init__(self, args):
        super().__init__()

        self.frames = {}
        self.layouts = {}
        self.labels = {}
        self.buttons = {}
        self.progress = {}
        self.separators = {}
        self.thread = {}
        self.request_password_thread = {}
        self.init_thread()

        self.widget = QWidget()
        self.layout = QVBoxLayout(self.widget)

        # Scroll Area
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setWidget(self.widget)
        self.setCentralWidget(self.scroll)

        self.setWindowTitle('PDF to PPTX Converter')
        self.setWindowIcon(QIcon(Settings.get_app_path() + '/assets/icon.png'))

        # Menu
        self.menu = MenuUI(self)
        self.menu.init_menu()

        # Load external style sheet
        style_sheet_path = Settings.get_app_path() + "/assets/styles.qss"
        with open(style_sheet_path, "r") as f:
            style_sheet = f.read()
            self.widget.setStyleSheet(style_sheet)

        self.text = QtWidgets.QLabel("Перетягніть файл(и) сюди\nабо натисніть щоб обрати")
        self.text.setAlignment(Qt.AlignCenter)
        self.text.setObjectName('mainLabel')
        self.layout.addWidget(self.text)
        self.layout.setStretchFactor(self.text, 1)

        self.setAcceptDrops(True)
        self.mousePressEvent = self.on_click

        self.resize(500, 600)
        self.show()

        if len(args) > 1:
            self.validate_files(args)

    def on_click(self, event):
        if event.button() == Qt.LeftButton:
            self.open_file()

    def open_file(self):
        fd = QFileDialog(self)
        fd.setFileMode(fd.FileMode.ExistingFiles)
        fd.setWindowTitle('Оберіть PDF файл(и)')
        fd.setNameFilter("PDF файл(и) (*.pdf)")
        fd.setViewMode(QFileDialog.ViewMode.List)
        if fd.exec():
            files = fd.selectedFiles()
            self.validate_files(files)

    def dragEnterEvent(self, event):
        # Accept the event if it has a file or files
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        # Handle the dropped files
        files = [url.toLocalFile() for url in event.mimeData().urls()]
        self.validate_files(files)

    def init_thread(self):
        self.thread[0] = WorkerThread()
        self.thread[0].file_process_start.connect(self.update_gui_on_file_process)
        self.thread[0].file_process_progress.connect(self.update_gui_on_convertion)
        self.thread[0].file_process_end.connect(self.update_gui_on_file_process_end)
        self.thread[0].file_process_failed.connect(self.update_gui_on_file_process_failed)
        self.file_added.connect(self.thread[0].update_file_list)

    def validate_files(self, files):
        validated_files = Validator.validate(files)
        if validated_files:
            self.filter_encrypted_files(validated_files)

    def filter_encrypted_files(self, files):
        not_encrypted_files = list()
        for file in files:
            if not file.encrypted or file.password:
                not_encrypted_files.append(file)
            else:
                self.create_password_thread(file)
        self.process_files(not_encrypted_files)

    def process_files(self, files):
        self.file_added.emit(files)
        self.update_gui_on_start(files)
        if not self.thread[0].isRunning():
            self.thread[0].start()

    def update_gui_on_start(self, files):
        for file in files:

            index = len(self.frames)
            self.frames[index] = QWidget(self)
            self.frames[index].setObjectName('fileFrame')
            self.layouts[index] = QGridLayout(self.frames[index])
            self.frames[index].setLayout(self.layouts[index])

            self.labels[index] = {}

            self.labels[index]['name'] = QLabel(file.name)
            self.labels[index]['name'].setObjectName('fileName')

            self.labels[index]['size'] = QLabel(f"Розмір файлу: {file.size} MB")
            self.labels[index]['size'].setObjectName('fileSize')

            self.labels[index]['slides'] = QLabel(f"Слайдів: {file.slides}")
            self.labels[index]['slides'].setObjectName('fileSlides')

            self.labels[index]['status'] = QLabel('В черзі')
            self.labels[index]['status'].setObjectName('fileStatus')

            self.progress[index] = QProgressBar(self)

            self.layouts[index].addWidget(self.labels[index]['name'], 0, 0, alignment=Qt.AlignmentFlag.AlignLeft)
            self.layouts[index].addWidget(self.progress[index], 0, 1, 2, 1, alignment=Qt.AlignmentFlag.AlignVCenter)
            self.layouts[index].addWidget(self.labels[index]['size'], 1, 0, alignment=Qt.AlignmentFlag.AlignLeft)
            self.layouts[index].addWidget(self.labels[index]['slides'], 2, 0, alignment=Qt.AlignmentFlag.AlignLeft)
            self.layouts[index].addWidget(self.labels[index]['status'], 2, 1, alignment=Qt.AlignmentFlag.AlignCenter)

            self.layout.insertWidget(self.layout.count() - 1, self.frames[index])
            self.layout.setStretchFactor(self.frames[index], 0)

    def update_gui_on_file_process(self, index):
        self.labels[index]['status'].setText("Триває обробка файлу...")
        self.labels[index]['status'].setObjectName('fileStatusProcessing')
        self.labels[index]['status'].style().unpolish(self.labels[index]['status'])
        self.labels[index]['status'].style().polish(self.labels[index]['status'])
        self.labels[index]['status'].update()

    def update_gui_on_convertion(self, index, current, total):
        self.progress[index].setMaximum(total)
        self.progress[index].setFormat('%v/%m')
        self.progress[index].setValue(current)
        self.labels[index]['status'].setObjectName('fileStatusConverting')
        self.labels[index]['status'].style().unpolish(self.labels[index]['status'])
        self.labels[index]['status'].style().polish(self.labels[index]['status'])
        self.labels[index]['status'].update()
        self.labels[index]['status'].setText("Конвертуємо слайди")

    def update_gui_on_file_process_end(self, index, time_spent, path):
        self.buttons[index] = QPushButton(QIcon(Settings.get_app_path() + '/assets/folder-open-regular.png'), f"Завершено ({time_spent:.2f}с)")
        self.buttons[index].setObjectName('fileStatusFinished')
        self.buttons[index].clicked.connect(lambda: self.on_file_open_click(path))
        self.layouts[index].addWidget(self.buttons[index], 2, 1, alignment=Qt.AlignmentFlag.AlignCenter)
        self.labels[index]['status'].hide()

    def update_gui_on_file_process_failed(self, index, message):
        self.labels[index]['status'].setText(message)
        self.labels[index]['status'].setObjectName('fileStatusFailed')
        self.labels[index]['status'].style().unpolish(self.labels[index]['status'])
        self.labels[index]['status'].style().polish(self.labels[index]['status'])
        self.labels[index]['status'].update()

    @staticmethod
    def get_file_name(path):
        result = os.path.basename(path)
        return result

    @staticmethod
    def on_file_open_click(path):
        path = os.path.abspath(path)
        if sys.platform == 'darwin':  # macOS
            subprocess.Popen(['open', '--reveal', path])
        elif sys.platform in ("win32", "cygwin", "msys"):  # Windows
            subprocess.Popen(['explorer', '/select,', path])

    def show_password_dialog(self, file):
        dialog = QtWidgets.QInputDialog(self)
        dialog.setInputMode(QtWidgets.QInputDialog.InputMode.TextInput)
        dialog.resize(300, 100)
        file.password, ok = dialog.getText(self, "Пароль для PDF", f"Введіть пароль для файлу {file.name}:", QtWidgets.QLineEdit.EchoMode.Password)
        self.process_encrypted_file(file, ok)

    def create_password_thread(self, file):
        self.request_password_thread = RequestPasswordThread()
        self.request_password_thread.show_password_dialog.connect(self.show_password_dialog)
        self.terminate_password_thread.connect(self.request_password_thread.terminate_thread)
        self.encrypted_file_added.connect(self.request_password_thread.added_encrypted_file)
        self.encrypted_file_added.emit(file)
        self.request_password_thread.start()

    def process_encrypted_file(self, file, ok):
        if ok:
            file.load_pdf()
            if not file.encrypted:
                self.filter_encrypted_files({file})
            else:
                QMessageBox.critical(self, "Документ захищений паролем", "Неправильний пароль!")

        else:
            print('Canceled')
        self.terminate_password_thread.emit()

    def quit(self):
        self.destroy()
        return sys.exit()
