from pdf2image import pdfinfo_from_path
from pdf2image.exceptions import PDFPageCountError
from classes.settings import Settings
from classes.exceptions.incorrect_password_error import PDFIncorrectPasswordError


class InfoHandler:

    @staticmethod
    def get_pdf_metadata(file, password=None):
        data = {}
        try:
            data = pdfinfo_from_path(file, poppler_path=Settings.get_poppler_path(), userpw=password)
        except PDFPageCountError as e:
            if 'Incorrect password' in str(e):
                raise PDFIncorrectPasswordError

        return data
