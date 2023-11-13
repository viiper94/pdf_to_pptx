import os
from colorama import Fore


class Validator:

    @staticmethod
    def validate(files):
        validated_files = list()
        for file in files:
            if Validator.is_pdf_file(file):
                validated_files.append(file)
        return tuple(validated_files)

    @staticmethod
    def is_pdf_file(file):
        _, extension = os.path.splitext(file)
        return extension.lower() == ".pdf"
