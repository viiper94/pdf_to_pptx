import os
from colorama import Fore


class Validator:

    @staticmethod
    def validate(files):
        validated_files = list()
        for file in files:
            if not Validator.is_pdf_file(file):
                print(Fore.RED + f"Файл {file} не PDF документ. Пропускаємо!")
            else:
                validated_files.append(file)
        return tuple(validated_files)

    @staticmethod
    def is_pdf_file(file):
        _, extension = os.path.splitext(file)
        return extension.lower() == ".pdf"
