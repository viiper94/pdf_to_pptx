import os
import sys
import subprocess

from PySide6 import QtWidgets
from PySide6.QtWidgets import (QFileDialog, QWidget, QLabel, QProgressBar, QGridLayout,
                               QVBoxLayout, QScrollArea, QMainWindow, QPushButton)
from PySide6.QtCore import Qt, Signal, QUrl
from PySide6.QtGui import QIcon, QAction, QActionGroup, QDesktopServices
from classes.worker import WorkerThread
from classes.validator import Validator
from classes.info_handler import InfoHandler
from classes.settings import Settings
from classes.exceptions.incorrect_password_error import PDFIncorrectPasswordError


class QtApp(QMainWindow):

    file_added = Signal(list)
    settings_changed = Signal(Settings)

    def __init__(self, args):
        super().__init__()

        self.settings = Settings
        self.frames = {}
        self.layouts = {}
        self.labels = {}
        self.buttons = {}
        self.progress = {}
        self.separators = {}
        self.thread = {}
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

        # Menu bar
        self.menu_bar = self.menuBar()
        self.file_menu = self.menu_bar.addMenu('&Конвертор')
        self.settings_menu = self.menu_bar.addMenu('&Налаштування')
        self.info_menu = self.menu_bar.addMenu('&Інфо')
        self.init_menu()

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
            validated_files = Validator.validate(args)
            if validated_files:
                self.pack_validated_files(validated_files)

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
            validated_files = Validator.validate(files)
            if validated_files:
                self.pack_validated_files(validated_files)

    def dragEnterEvent(self, event):
        # Accept the event if it has a file or files
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        # Handle the dropped files
        files = [url.toLocalFile() for url in event.mimeData().urls()]
        validated_files = Validator.validate(files)
        if validated_files:
            self.pack_validated_files(validated_files)

    def init_thread(self):
        self.thread[0] = WorkerThread()
        self.thread[0].file_process_start.connect(self.update_gui_on_file_process)
        self.thread[0].file_process_progress.connect(self.update_gui_on_convertion)
        self.thread[0].file_process_end.connect(self.update_gui_on_file_process_end)
        self.thread[0].file_process_failed.connect(self.update_gui_on_file_process_failed)
        self.file_added.connect(self.thread[0].update_file_list)

    def pack_validated_files(self, files):
        packed_files = []
        for file in files:
            packed_files.append({'path': file, 'password': None})
        return self.process_files(packed_files)

    def process_files(self, files):
        self.file_added.emit(files)
        self.update_gui_on_start(files)
        if not self.thread[0].isRunning():
            self.thread[0].start()

    def update_gui_on_start(self, files):
        for file_path in files:
            index = len(self.frames)
            self.frames[index] = QWidget(self)
            self.frames[index].setObjectName('fileFrame')
            self.layouts[index] = QGridLayout(self.frames[index])
            self.frames[index].setLayout(self.layouts[index])

            self.labels[index] = {}

            size = os.stat(file['path']).st_size / (1024 * 1024)
            formatted_size = f"{size:.2f}"

            self.labels[index]['name'] = QLabel(self.get_file_name(file['path']))
            self.labels[index]['name'].setObjectName('fileName')

            self.labels[index]['size'] = QLabel(f"Розмір файлу: {formatted_size} MB")
            self.labels[index]['size'].setObjectName('fileSize')

            self.labels[index]['slides'] = QLabel(f"Слайдів: {pdf['Pages']}")
            self.labels[index]['slides'].setObjectName('fileSlides')

            self.labels[index]['status'] = QLabel('В черзі')
            self.labels[index]['status'].setObjectName('fileStatus')

            self.labels[index]['done'] = False

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
        self.buttons[index] = QPushButton(QIcon(Settings.get_app_path() + '/assets/folder-open-regular.png'), f"Завершено ({time_spent}с)")
        self.buttons[index].setObjectName('fileStatusFinished')
        self.buttons[index].clicked.connect(lambda: self.on_file_open_click(path))
        self.layouts[index].addWidget(self.buttons[index], 2, 1, alignment=Qt.AlignmentFlag.AlignCenter)
        self.labels[index]['status'].hide()
        self.labels[index]['done'] = True

    def update_gui_on_file_process_failed(self, index, message):
        self.labels[index]['status'].setText(message)
        self.labels[index]['status'].setObjectName('fileStatusFailed')
        self.labels[index]['status'].style().unpolish(self.labels[index]['status'])
        self.labels[index]['status'].style().polish(self.labels[index]['status'])
        self.labels[index]['status'].update()

    def get_file_name(self, path):
        result = os.path.basename(path)
        return result

    def on_file_open_click(self, path):
        path = os.path.abspath(path)
        if sys.platform.startswith('darwin'):  # macOS
            subprocess.Popen(['open', '--reveal', path])
        elif sys.platform.startswith('win'):  # Windows
            subprocess.Popen(['explorer', '/select,', path])

    def init_menu(self):
        # file - open menu item
        open_action = QAction(QIcon(Settings.get_app_path() + '/assets/file-pdf-regular.svg'), '&Додати файл(и)', self)
        open_action.triggered.connect(self.open_file)
        open_action.setShortcut('Ctrl+O')
        self.file_menu.addAction(open_action)

        # file - clear menu item
        clear_action = QAction(QIcon(Settings.get_app_path() + '/assets/minus-solid.svg'), '&Очистити список', self)
        clear_action.triggered.connect(self.clear_file_list)
        self.file_menu.addAction(clear_action)

        self.file_menu.addSeparator()

        # file - exit menu item
        exit_action = QAction(QIcon(Settings.get_app_path() + '/assets/xmark-solid.svg'), '&Вийти', self)
        exit_action.setShortcut('Alt+F4')
        exit_action.triggered.connect(self.quit)
        self.file_menu.addAction(exit_action)

        # settings - dpi text menu item
        res_action = QAction('&Роздільна здатність', self, disabled=True)
        self.settings_menu.addAction(res_action)

        resolution_group = QActionGroup(self)
        # settings - fhd resolution menu item
        fhd_action = QAction('&Full HD (1080px)', self, checkable=True, checked=self.settings.resolution == 1920)
        fhd_action.setActionGroup(resolution_group)
        fhd_action.triggered.connect(self.on_resolution_changed)
        self.settings_menu.addAction(fhd_action)

        # settings - qhd resolution menu item
        qhd_action = QAction('&Quad HD (1440px)', self, checkable=True, checked=self.settings.resolution == 2560)
        qhd_action.setActionGroup(resolution_group)
        qhd_action.triggered.connect(self.on_resolution_changed)
        self.settings_menu.addAction(qhd_action)

        # settings - uhd resolution menu item
        uhd_action = QAction('&Ultra HD (2160px)', self, checkable=True, checked=self.settings.resolution == 3840)
        uhd_action.setActionGroup(resolution_group)
        uhd_action.triggered.connect(self.on_resolution_changed)
        self.settings_menu.addAction(uhd_action)

        # settings - original resolution menu item
        original_action = QAction('&Оригінальний розмір', self, checkable=True, checked=self.settings.resolution == None)
        original_action.setActionGroup(resolution_group)
        original_action.triggered.connect(self.on_resolution_changed)
        self.settings_menu.addAction(original_action)

        self.settings_menu.addSeparator()

        # settings - dpi text menu item
        dpi_action = QAction('&DPI', self, disabled=True)
        self.settings_menu.addAction(dpi_action)

        dpi_group = QActionGroup(self)
        # settings - 100 dpi menu item
        dpi_action_100 = QAction('&100 DPI', self, checkable=True, checked=self.settings.dpi == 100)
        dpi_action_100.setActionGroup(dpi_group)
        dpi_action_100.triggered.connect(self.on_dpi_changed)
        self.settings_menu.addAction(dpi_action_100)

        # settings - 200 dpi menu item
        dpi_action_200 = QAction('&200 DPI', self, checkable=True, checked=self.settings.dpi == 200)
        dpi_action_200.setActionGroup(dpi_group)
        dpi_action_200.triggered.connect(self.on_dpi_changed)
        self.settings_menu.addAction(dpi_action_200)

        # settings - 300 dpi menu item
        dpi_action_300 = QAction('&300 DPI', self, checkable=True, checked=self.settings.dpi == 300)
        dpi_action_300.setActionGroup(dpi_group)
        dpi_action_300.triggered.connect(self.on_dpi_changed)
        self.settings_menu.addAction(dpi_action_300)

        self.settings_menu.addSeparator()

        # settings - aspect text menu item
        aspect_action = QAction('&Співвідношення сторін', self, disabled=True)
        self.settings_menu.addAction(aspect_action)

        aspect_group = QActionGroup(self)
        # settings - auto aspect menu item
        aspect_action_auto = QAction('&Автоматично', self, checkable=True, checked=self.settings.aspect == 'auto')
        aspect_action_auto.setActionGroup(aspect_group)
        aspect_action_auto.triggered.connect(self.on_aspect_changed)
        self.settings_menu.addAction(aspect_action_auto)

        # settings - 16x9 aspect menu item
        aspect_action_16 = QAction('&16:9', self, checkable=True, checked=self.settings.aspect == '16x9')
        aspect_action_16.setActionGroup(aspect_group)
        aspect_action_16.triggered.connect(self.on_aspect_changed)
        self.settings_menu.addAction(aspect_action_16)

        # settings - 4x3 aspect menu item
        aspect_action_4 = QAction('&4:3', self, checkable=True, checked=self.settings.aspect == '4x3')
        aspect_action_4.setActionGroup(aspect_group)
        aspect_action_4.triggered.connect(self.on_aspect_changed)
        self.settings_menu.addAction(aspect_action_4)

        self.settings_menu.addSeparator()

        # settings - output text menu item
        output_action = QAction('&Конвертувати в', self, disabled=True)
        self.settings_menu.addAction(output_action)

        output_group = QActionGroup(self)
        # settings - pptx output menu item
        output_action_pptx = QAction('&PPTX', self, checkable=True, checked=self.settings.output == 'pptx')
        output_action_pptx.setActionGroup(output_group)
        output_action_pptx.triggered.connect(self.on_output_changed)
        self.settings_menu.addAction(output_action_pptx)

        # settings - jpg output menu item
        output_action_jpg = QAction('&JPEG', self, checkable=True, checked=self.settings.aspect == 'jpg')
        output_action_jpg.setActionGroup(output_group)
        output_action_jpg.triggered.connect(self.on_output_changed)
        self.settings_menu.addAction(output_action_jpg)

        # info - repo menu item
        repo_action = QAction('&GitHub', self)
        repo_action.triggered.connect(self.open_github)
        self.info_menu.addAction(repo_action)

        # info - version menu item
        version_action = QAction('&v0.9', self, disabled=True)
        self.info_menu.addAction(version_action)

        self.file_menu.addSeparator()

        self.settings_changed.connect(self.thread[0].update_settings)

    def on_resolution_changed(self):
        action = self.sender()
        if action.isChecked():
            text = action.text()
            self.settings.change_resolution(self.settings, text)
            self.settings_changed.emit(self.settings)

    def on_dpi_changed(self):
        action = self.sender()
        if action.isChecked():
            text = action.text()
            self.settings.change_dpi(self.settings, text)
            self.settings_changed.emit(self.settings)

    def on_aspect_changed(self):
        action = self.sender()
        if action.isChecked():
            text = action.text()
            self.settings.change_aspect(self.settings, text)
            self.settings_changed.emit(self.settings)

    def on_output_changed(self):
        action = self.sender()
        if action.isChecked():
            text = action.text()
            self.settings.change_output(self.settings, text)
            self.settings_changed.emit(self.settings)

    def clear_file_list(self):
        for i, item in enumerate(self.labels):
            if self.labels[i]['done']:
                self.frames[i].hide()

    def open_github(self):
        QDesktopServices.openUrl(QUrl("https://github.com/viiper94/pdf_to_pptx"))

    def quit(self):
        self.destroy()
        return sys.exit()
