import time

from PySide6.QtCore import Signal, QThread
from classes.convertor import Convertor


class WorkerThread(QThread):

    file_process_start = Signal(int)
    file_process_progress = Signal(int, int, int)
    file_process_end = Signal(int, int)

    def __init__(self):
        super().__init__()
        self.files = {}

    def run(self):
        index = 0
        while index < len(self.files):
            item = self.files[index]
            if not item['done']:
                convertor = Convertor(index, item['path'], self)
                convertor.convert()
                self.files[index]['done'] = True
            index += 1

    def update_file_list(self, new_files):
        for file in new_files:
            index = len(self.files)
            self.files[index] = {}
            self.files[index]['path'] = file
            self.files[index]['done'] = False
