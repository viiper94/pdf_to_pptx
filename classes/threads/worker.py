from PySide6.QtCore import Signal, QThread
from classes.convertor import Convertor
from classes.settings import Settings


class WorkerThread(QThread):

    file_process_start = Signal(int)
    file_process_progress = Signal(int, int, int)
    file_process_end = Signal(int, float, str)
    file_process_failed = Signal(int, str)
    file_process_canceled = Signal(int)

    def __init__(self):
        super().__init__()
        self.files = {}
        self.settings = Settings()

    def run(self):
        index = 0
        while index < len(self.files):
            item = self.files[index]
            if not item.status == 2:
                convertor = Convertor(
                    index=index,
                    file=item,
                    thread=self,
                    settings=self.settings)
                convertor.convert()
            index += 1

    def update_file_list(self, new_files):
        for file in new_files:
            index = len(self.files)
            self.files[index] = file

    def update_settings(self, settings):
        self.settings = settings

    def cancel_conversion(self, index):
        if self.files[index].status == 0:
            self.file_process_canceled.emit(index)
        self.files[index].status = 5
