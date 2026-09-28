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
from classes.theme import get_system_theme
from classes.logger import LoggerWindow
from classes.i18n import i18n


class QtApp(QMainWindow):

    encrypted_file_added = Signal(File)
    terminate_password_thread = Signal()
    file_added = Signal(list)
    cancel_conversion = Signal(int)

    width = 500
    height = 600

    def __init__(self, args):
        super().__init__()

        self.frames = {}
        self.worker_thread = None
        self.request_password_thread = None
        self.init_thread()

        self.logger = LoggerWindow(self)

        self.widget = QWidget()
        self.layout = QVBoxLayout(self.widget)

        # Scroll Area
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setWidget(self.widget)
        self.setCentralWidget(self.scroll)

        self.setWindowTitle(i18n.t('PDF to PPTX Converter'))
        self.setWindowIcon(QIcon(Settings.get_app_path() + '/assets/icon.png'))

        self.theme = get_system_theme()

        # Menu
        self.menu = MenuUI(self)
        self.menu.init_menu()
        self.load_stylesheet(self.theme)

        self.text = QtWidgets.QLabel(i18n.t("Drag files here \n to start conversion"))
        self.text.setAlignment(Qt.AlignCenter)
        self.text.setObjectName('mainLabel')
        self.layout.addWidget(self.text)
        self.layout.setStretchFactor(self.text, 1)

        self.setAcceptDrops(True)
        # self.text.mousePressEvent = self.on_click

        self.resize(self.width, self.height)
        self.move(
            self.screen().availableGeometry().right() - 20 - self.width,
            self.screen().availableGeometry().bottom() - 50 - self.height)
        self.show()

        if len(args) > 1:
            self.validate_files(args)

        self.logger.log("Application started.")

    def load_stylesheet(self, theme_name: str):
        path = f"{Settings.get_app_path()}/assets/styles/{theme_name}.qss"
        try:
            with open(path, 'r') as file:
                self.setStyleSheet(file.read())
        except FileNotFoundError:
            self.logger.log(f"Stylesheet not found!")

    # def on_click(self, event):
    #     if event.button() == Qt.LeftButton:
    #         self.open_file()

    def open_file(self):
        fd = QFileDialog(self)
        fd.setFileMode(fd.FileMode.ExistingFiles)
        fd.setWindowTitle(i18n.t('Choose PDF file(s)'))
        fd.setNameFilter(i18n.t("PDF file(s) (*.pdf)"))
        fd.setViewMode(QFileDialog.ViewMode.List)
        if fd.exec():
            files = fd.selectedFiles()
            self.validate_files(files)

    def dragEnterEvent(self, event):
        self.widget.setObjectName('widgetDrag')
        self.widget.style().unpolish(self.widget)
        self.widget.style().polish(self.widget)
        # Accept the event if it has a file or files
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dragLeaveEvent(self, event):
        self.widget.setObjectName('')
        self.widget.style().unpolish(self.widget)
        self.widget.style().polish(self.widget)

    def dropEvent(self, event):
        self.widget.setObjectName('')
        self.widget.style().unpolish(self.widget)
        self.widget.style().polish(self.widget)
        # Handle the dropped files
        files = [url.toLocalFile() for url in event.mimeData().urls()]
        self.validate_files(files)

    def init_thread(self):
        self.worker_thread = WorkerThread(self)
        self.worker_thread.file_process_start.connect(self.update_gui_on_file_process)
        self.worker_thread.file_process_progress.connect(self.update_gui_on_convertion)
        self.worker_thread.file_process_end.connect(self.update_gui_on_file_process_end)
        self.worker_thread.file_process_failed.connect(self.update_gui_on_file_process_failed)
        self.worker_thread.file_process_canceled.connect(self.update_gui_on_file_process_canceled)
        self.file_added.connect(self.worker_thread.update_file_list)
        self.cancel_conversion.connect(self.worker_thread.cancel_conversion)

    def validate_files(self, files):
        validated_files, failed_files = Validator.validate(files, settings=self.worker_thread.settings)
        if validated_files:
            self.filter_encrypted_files(validated_files)
            self.logger.log(f"{len(validated_files)} validated files 🗸")
        if failed_files:
            self.logger.log(f"{len(failed_files)} failed files ✖")
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setText(i18n.t("Not a PDF or corrupted file:"))
            msg.setInformativeText("\n".join(failed_files))
            msg.setWindowIcon(QIcon(Settings.get_app_path() + '/assets/icon.png'))
            msg.setWindowTitle(i18n.t("Error"))
            msg.setStandardButtons(QMessageBox.StandardButton.Ok)
            msg.exec()

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
            self.logger.log("Worker thread started.")
        if self.request_password_thread:
            self.request_password_thread.start()
            self.logger.log("Request password thread started.")

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
        file.password, ok = dialog.getText(self, i18n.t("Password for PDF"), f"{i18n.t('Enter password for file')} {file.name}:", QtWidgets.QLineEdit.EchoMode.Password)
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
                self.logger.log(f"Password correct for file {file.name} ✓")
                self.filter_encrypted_files({file})
            else:
                self.logger.log(f"Incorrect password for file {file.name} ✖")
                msg = QMessageBox(self)
                msg.setIcon(QMessageBox.Icon.Critical)
                msg.setText(i18n.t("Wrong password!"))
                msg.setWindowTitle(i18n.t("Document is encrypted"))
                msg.setStandardButtons(QMessageBox.StandardButton.Ok)
                msg.exec()
        else:
            self.logger.log(f"Password request canceled for file {file.name}")
        self.terminate_password_thread.emit()

    def update_language(self, lang):
        i18n.set_language(lang)
        self.translate_ui()

    def translate_ui(self):
        # QtApp
        self.setWindowTitle(i18n.t('PDF to PPTX Converter'))
        self.text.setText(i18n.t("Drag files here \n to start conversion"))
        # MenuUi
        self.menu.destroy_menu()
        self.menu.init_menu()
        # FileFrames
        for i, frame in self.frames.items():
            frame.translate_frame()
        # Logger
        self.logger.setWindowTitle(i18n.t("Logs"))

    def closeEvent(self, event):
        self.quit()

    def quit(self):
        self.worker_thread.terminate()
        self.destroy()
        return sys.exit()
