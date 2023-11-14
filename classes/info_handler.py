from pdf2image import pdfinfo_from_path
from classes.settings import Settings


class InfoHandler:

    @staticmethod
    def get_pdf_metadata(file):
        return pdfinfo_from_path(file, poppler_path=Settings.get_poppler_path())
