from pdf2image import pdfinfo_from_path
from classes.convertor import Convertor


class InfoHandler:

    @staticmethod
    def get_pdf_metadata(file):
        return pdfinfo_from_path(file, poppler_path=Convertor.poppler_path)
