import pypdfium2 as pdfium
from pypdfium2 import PdfiumError

from classes.exceptions.incorrect_password_error import PDFIncorrectPasswordError


class InfoHandler:

    @staticmethod
    def get_pdf_metadata(file, password=None):
        pdf = None

        try:
            pdf = pdfium.PdfDocument(file, password=password)
            page = pdf[0]
            width_pt, height_pt = page.get_size()
            return {'Pages': len(pdf), 'Width': width_pt, 'Height': height_pt}

        except PdfiumError as e:
            if 'Incorrect password' in str(e):
                raise PDFIncorrectPasswordError

        return pdf
