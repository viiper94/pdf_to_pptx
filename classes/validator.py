import os
from classes.pdf_file import File


class Validator:

    @staticmethod
    def validate(files, settings=None):
        validated_files = list()
        failed_files = list()
        for file in files:
            if Validator.is_pdf_file(file):
                validated_files.append(File(file, settings=settings))
            else:
                failed_files.append(file)
        return validated_files, failed_files

    @staticmethod
    def is_pdf_file(file_path):
        """
        Properly checks if a file is a PDF by reading its content,
        regardless of the file extension.

        1. Checks if the path points to an actual, readable file.
        2. Reads the first 5 bytes to check for the PDF magic number ('%PDF-').
        """
        # 1. First, ensure the path is a file and not a directory.
        if not os.path.isfile(file_path):
            return False

        # 2. Check the magic number for definitive validation.
        try:
            with open(file_path, 'rb') as f:
                # The magic number for PDF files is the byte sequence b'%PDF-'
                return f.read(5) == b'%PDF-'
        except (IOError, PermissionError):
            # The file might exist but be unreadable (e.g., permissions issue),
            # so we treat it as invalid.
            return False
