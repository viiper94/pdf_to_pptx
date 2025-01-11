import time
from PySide6.QtCore import Signal, QThread
from classes.pdf_file import File


class RequestPasswordThread(QThread):

    show_password_dialog = Signal(File)

    def __init__(self):
        super().__init__()
        self.encrypted_files = list()

    def run(self):
        for file in self.encrypted_files:
            self.show_password_dialog.emit(file)

    def added_encrypted_file(self, file):
        self.encrypted_files.append(file)

    def terminate_thread(self):
        self.terminate()
