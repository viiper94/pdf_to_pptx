import time
from PySide6.QtCore import Signal, QThread


class RequestPasswordThread(QThread):

    show_password_dialog = Signal(str)
    process_encrypted_file = Signal(str, str)

    def __init__(self):
        super().__init__()
        self.encrypted_files = {}

    def run(self):
        for index in self.encrypted_files:
            self.show_password_dialog.emit(self.encrypted_files[index]['path'])
            # wait for password from user input
            while self.encrypted_files[index]['password'] is None or self.encrypted_files[index]['password'] == '':
                time.sleep(0.3)
                pass
            self.process_encrypted_file.emit(
                self.encrypted_files[index]['path'],
                self.encrypted_files[index]['password'])

    def added_encrypted_file(self, file_path):
        index = len(self.encrypted_files)
        self.encrypted_files[index] = {}
        self.encrypted_files[index]['path'] = file_path
        self.encrypted_files[index]['password'] = None

    def update_password(self, file_path, password):
        for index in self.encrypted_files:
            if self.encrypted_files[index]['path'] == file_path:
                self.encrypted_files[index]['password'] = password
                break

    def terminate_thread(self):
        self.terminate()
