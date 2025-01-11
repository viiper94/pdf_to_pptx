import os
import pypdfium2 as pdfium


class File:

    path = ''
    path_no_ext = ''
    name = ''
    name_no_ext = ''
    size = 0                   # in MB
    slides = None
    width = None
    height = None
    aspect_ratio = None
    # index = 0
    status = 0                  # 0 - in queue, 1 - in progress, 2 - finished
    doc = None
    encrypted = False
    password = None
    converted_path = ''

    def __init__(self, path, password=None):
        self.path = path
        self.path_no_ext = os.path.splitext(path)[0]
        self.password = password
        self.name = os.path.basename(path)
        self.name_no_ext = os.path.splitext(self.name)[0]
        self.size = self.get_file_size()
        self.load_pdf()

    def load_pdf(self):
        try:
            self.doc = pdfium.PdfDocument(self.path, password=self.password)
            self.slides = len(self.doc)
            self.width, self.height = self.doc[0].get_size()
            self.aspect_ratio = self.width / self.height
            self.encrypted = False
        except pdfium.PdfiumError as e:
            if 'Incorrect password' in str(e):
                self.encrypted = True

    def get_file_size(self):
        size = os.stat(self.path).st_size / (1024 * 1024)
        return f"{size:.2f}"

    def set_password(self, password):
        self.password = password
        self.load_pdf()
