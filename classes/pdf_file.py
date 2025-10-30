import os
import pypdfium2 as pdfium


class File:

    def __init__(self, path, password=None):

        self.path = path
        self.path_no_ext = os.path.splitext(path)[0]
        self.password = password
        self.name = os.path.basename(path)
        self.name_no_ext = os.path.splitext(self.name)[0]
        self.dir = os.path.dirname(path)
        self.size = self.get_file_size()                    # in MB
        self.status = 0                                     # 0 - in queue, 1 - processing, 2 - converting, 3 - finished, 4 - failed, 5 - canceled
        self.doc = None
        self.slides = 0
        self.width = 0
        self.height = 0
        self.aspect_ratio = 0
        self.encrypted = False
        self.load_pdf()

    def load_pdf(self):
        try:
            self.doc = pdfium.PdfDocument(self.path, password=self.password)
            self.slides = len(self.doc)
            self.width, self.height = self.doc[0].get_size()
            self.aspect_ratio = self.width / self.height
            self.encrypted = False
        except pdfium.PdfiumError as e:
            self.encrypted = 'Incorrect password' in str(e)

    def get_file_size(self):
        size = os.stat(self.path).st_size / (1024 * 1024)
        return f"{size:.2f}"

    def set_password(self, password):
        self.password = password
        self.load_pdf()
