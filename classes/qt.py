import sys

from PySide6 import QtWidgets
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QFileDialog, QWidget, QMessageBox, QVBoxLayout, QScrollArea, QMainWindow

from classes.threads.request_password import RequestPasswordThread
from classes.threads.worker import WorkerThread
from classes.validator import Validator
from classes.settings import Settings
from classes.ui.menu import MenuUI
from classes.pdf_file import File
from classes.ui.fileframe import FileFrame


class QtApp(QMainWindow):

    encrypted_file_added = Signal(File)
    terminate_password_thread = Signal()
    file_added = Signal(list)
    cancel_conversion = Signal(int)

    def __init__(self, args):
        super().__init__()

        self.frames = {}
        self.worker_thread = None
        self.request_password_thread = None
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
        self.text.mousePressEvent = self.on_click

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
        self.worker_thread = WorkerThread()
        self.worker_thread.file_process_start.connect(self.update_gui_on_file_process)
        self.worker_thread.file_process_progress.connect(self.update_gui_on_convertion)
        self.worker_thread.file_process_end.connect(self.update_gui_on_file_process_end)
        self.worker_thread.file_process_failed.connect(self.update_gui_on_file_process_failed)
        self.worker_thread.file_process_canceled.connect(self.update_gui_on_file_process_canceled)
        self.file_added.connect(self.worker_thread.update_file_list)
        self.cancel_conversion.connect(self.worker_thread.cancel_conversion)

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
                if not self.request_password_thread:
                    self.create_password_thread()
                self.encrypted_file_added.emit(file)
        self.process_files(not_encrypted_files)

    def process_files(self, files):
        self.file_added.emit(files)
        self.update_gui_on_start(files)
        if not self.worker_thread.isRunning():
            self.worker_thread.start()
        if self.request_password_thread:
            self.request_password_thread.start()

    def update_gui_on_start(self, files):
        for file in files:
            index = len(self.frames)
            self.frames[index] = FileFrame(self, index, file)
            self.layout.insertWidget(self.layout.count() - 1, self.frames[index].frame)
            self.layout.setStretchFactor(self.frames[index].frame, 0)

    def update_gui_on_file_process(self, index):
        self.frames[index].on_file_processing()

    def update_gui_on_convertion(self, index, current):
        self.frames[index].on_converting(current)

    def update_gui_on_file_process_end(self, index, time_spent, path):
        self.frames[index].on_finished(time_spent, path)

    def update_gui_on_file_process_failed(self, index):
        self.frames[index].on_failed()

    def update_gui_on_file_process_canceled(self, index):
        self.frames[index].on_canceled()

    def show_password_dialog(self, file):
        dialog = QtWidgets.QInputDialog(self)
        dialog.setInputMode(QtWidgets.QInputDialog.InputMode.TextInput)
        dialog.resize(300, 100)
        file.password, ok = dialog.getText(self, "Пароль для PDF", f"Введіть пароль для файлу {file.name}:", QtWidgets.QLineEdit.EchoMode.Password)
        self.process_encrypted_file(file, ok)

    def create_password_thread(self):
        self.request_password_thread = RequestPasswordThread()
        self.request_password_thread.show_password_dialog.connect(self.show_password_dialog)
        self.terminate_password_thread.connect(self.request_password_thread.terminate_thread)
        self.encrypted_file_added.connect(self.request_password_thread.added_encrypted_file)

    def process_encrypted_file(self, file, ok):
        if ok:
            file.load_pdf()
            if not file.encrypted:
                self.filter_encrypted_files({file})
            else:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Icon.Critical)
                msg.setText("Неправильний пароль!")
                msg.setWindowTitle("Документ захищений паролем")
                msg.setStandardButtons(QMessageBox.StandardButton.Ok)
                msg.exec()
        else:
            print('Canceled')
        self.terminate_password_thread.emit()

    def closeEvent(self, event):
        self.quit()

    def quit(self):
        self.worker_thread.terminate()
        self.destroy()
        return sys.exit()
