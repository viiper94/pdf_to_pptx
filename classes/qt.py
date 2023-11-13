import os
import sys

from PySide6 import QtWidgets, QtCore
from PySide6.QtWidgets import QFileDialog, QWidget, QLabel, QProgressBar, QGridLayout, QVBoxLayout, QScrollArea, QMainWindow
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon, QAction, QActionGroup
from classes.worker import WorkerThread
from classes.validator import Validator
from classes.info_handler import InfoHandler
from classes.settings import Settings


class QtApp(QMainWindow):

    file_added = Signal(list)
    settings_changed = Signal(Settings)

    def __init__(self, args):
        super().__init__()

        self.settings = Settings
        self.frames = {}
        self.layouts = {}
        self.labels = {}
        self.progress = {}
        self.separators = {}
        self.thread = {}
        self.init_thread()

        self.widget = QWidget()
        self.layout = QVBoxLayout(self)
        self.widget.setLayout(self.layout)

        # Scroll Area
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setWidget(self.widget)
        self.setCentralWidget(self.scroll)

        self.setWindowTitle('PDF to PPTX Converter')
        self.setWindowIcon(QIcon('./assets/icon.png'))
        self.widget.setStyleSheet('background-color: #2a2a2a')

        # Menu bar
        self.menu_bar = self.menuBar()
        self.file_menu = self.menu_bar.addMenu('&Конвертор')
        self.settings_menu = self.menu_bar.addMenu('&Налаштування')
        self.init_menu()

        self.text = QtWidgets.QLabel("Перетягніть файл(и) сюди\nабо натисніть щоб обрати")
        self.text.setAlignment(Qt.AlignCenter)
        self.text.setStyleSheet('font-size: 15px; font-family: "Sergoe"; color: #eee')
        self.layout.addWidget(self.text)
        self.layout.setStretchFactor(self.text, 1)

        self.setAcceptDrops(True)
        self.mousePressEvent = self.on_click

        self.resize(500, 600)
        self.show()

        if len(args) > 1:
            validated_files = Validator.validate(args)
            if validated_files:
                self.process_files(validated_files)

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
                self.process_files(validated_files)

    def dragEnterEvent(self, event):
        # Accept the event if it has a file or files
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        # Handle the dropped files
        files = [url.toLocalFile() for url in event.mimeData().urls()]
        validated_files = Validator.validate(files)
        if validated_files:
            self.process_files(validated_files)

    def init_thread(self):
        self.thread[0] = WorkerThread()
        self.thread[0].file_process_start.connect(self.update_gui_on_file_process)
        self.thread[0].file_process_progress.connect(self.update_gui_on_convertion)
        self.thread[0].file_process_end.connect(self.update_gui_on_file_process_end)
        self.file_added.connect(self.thread[0].update_file_list)

    def process_files(self, files):
        self.file_added.emit(files)
        self.update_gui_on_start(files)
        if not self.thread[0].isRunning():
            self.thread[0].start()


    def update_gui_on_start(self, files):
        for file_path in files:
            index = len(self.frames)
            self.frames[index] = QWidget(self)
            self.frames[index].setStyleSheet('background-color: transparent; border-bottom: 1px solid #363636')
            self.layouts[index] = QGridLayout(self.frames[index])
            self.frames[index].setLayout(self.layouts[index])

            self.labels[index] = {}

            pdf = InfoHandler.get_pdf_metadata(file_path)
            self.labels[index]['name'] = QLabel(self.get_file_name(file_path))
            self.labels[index]['name'].setStyleSheet('color: #eee; border: none; font-size: 16px')

            self.labels[index]['size'] = QLabel("Розмір файлу {:.2f} MB".format(int(pdf['File size'].split()[0]) / 10 ** 6))
            self.labels[index]['size'].setStyleSheet('color: #5d5d5d; border: none')

            self.labels[index]['slides'] = QLabel(f"Слайдів: {pdf['Pages']}")
            self.labels[index]['slides'].setStyleSheet('color: #5d5d5d; border: none')

            self.labels[index]['status'] = QLabel('В черзі')
            self.labels[index]['status'].setStyleSheet('color: #89898b; border: none')

            self.progress[index] = QProgressBar(self)
            self.progress[index].setStyleSheet('background-color: #363636; '
                                               'border: none; '
                                               'max-width: 200px; '
                                               'min-width: 150px; '
                                               'text-align: center;'
                                               'color: #eee')

            self.layouts[index].addWidget(self.labels[index]['name'], 0, 0, alignment=Qt.AlignmentFlag.AlignLeft)
            self.layouts[index].addWidget(self.progress[index], 0, 1, 2, 1, alignment=Qt.AlignmentFlag.AlignVCenter)
            self.layouts[index].addWidget(self.labels[index]['size'], 1, 0, alignment=Qt.AlignmentFlag.AlignLeft)
            self.layouts[index].addWidget(self.labels[index]['slides'], 2, 0, alignment=Qt.AlignmentFlag.AlignLeft)
            self.layouts[index].addWidget(self.labels[index]['status'], 2, 1, alignment=Qt.AlignmentFlag.AlignCenter)

            self.text.setText('')
            self.layout.insertWidget(self.layout.count() - 1, self.frames[index])
            self.layout.setStretchFactor(self.frames[index], 0)

    def update_gui_on_file_process(self, index):
        self.labels[index]['status'].setText("Триває обробка файлу...")
        self.labels[index]['status'].setStyleSheet('color: #e9a222; border: none')

    def update_gui_on_convertion(self, index, current, total):
        self.progress[index].setMaximum(total)
        self.progress[index].setFormat('%v/%m')
        self.progress[index].setValue(current)
        self.labels[index]['status'].setStyleSheet('color: #da1039; border: none')
        self.labels[index]['status'].setText("Конвертуємо слайди")

    def update_gui_on_file_process_end(self, index, time_spent):
        self.labels[index]['status'].setText(f"Завершено ({time_spent}с)")
        self.labels[index]['status'].setStyleSheet('color: green; border: none')

    def get_file_name(self, path):
        result = os.path.basename(path)
        return result

    def init_menu(self):
        # file - open menu item
        open_action = QAction(QIcon('./assets/open.png'), '&Додати файл(и)', self)
        open_action.triggered.connect(self.open_file)
        open_action.setShortcut('Ctrl+O')
        self.file_menu.addAction(open_action)

        # file - exit menu item
        exit_action = QAction(QIcon('./assets/exit.png'), '&Вийти', self)
        exit_action.setShortcut('Alt+F4')
        exit_action.triggered.connect(self.quit)
        self.file_menu.addAction(exit_action)

        resolution_group = QActionGroup(self)
        # settings - fhd resolution menu item
        fhd_action = QAction('&FullHD', self, checkable=True, checked=True)
        fhd_action.setActionGroup(resolution_group)
        fhd_action.triggered.connect(self.on_resolution_changed)
        self.settings_menu.addAction(fhd_action)

        # settings - fhd resolution menu item
        qhd_action = QAction('&2K', self, checkable=True)
        qhd_action.setActionGroup(resolution_group)
        qhd_action.triggered.connect(self.on_resolution_changed)
        self.settings_menu.addAction(qhd_action)

        # settings - fhd resolution menu item
        uhd_action = QAction('&4K', self, checkable=True)
        uhd_action.setActionGroup(resolution_group)
        uhd_action.triggered.connect(self.on_resolution_changed)
        self.settings_menu.addAction(uhd_action)

        self.settings_changed.connect(self.thread[0].update_settings)

    def on_resolution_changed(self):
        action = self.sender()
        if action.isChecked():
            text = action.text()
            self.settings.change_resolution(self.settings, text)
            self.settings_changed.emit(self.settings)

    def quit(self):
        self.destroy()
        return sys.exit()
