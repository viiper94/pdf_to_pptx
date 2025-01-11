from PySide6.QtCore import Signal, QThread
from classes.convertor import Convertor
from classes.settings import Settings


class WorkerThread(QThread):

    file_process_start = Signal(int)
    file_process_progress = Signal(int, int, int)
    file_process_end = Signal(int, float, str)
    file_process_failed = Signal(int, str)

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
                item.status = 2
            index += 1

    def update_file_list(self, new_files):
        for file in new_files:
            index = len(self.files)
            self.files[index] = file

    def update_settings(self, settings):
        self.settings = settings

    def remove_file(self, path):
        for index in self.files:
            if (self.files[index]['path'] == path
                    and not self.files[index]['done']
                    and self.files[index]['password'] is None):
                del self.files[index]
                break

        # reset indexes in self.files
        self.files = {i: value for i, value in enumerate(self.files.values())}
