import os
import re
import time
from io import BytesIO
from pdf2image import convert_from_path
from pdf2image import pdfinfo_from_path
from pptx import Presentation
from pptx.util import Inches
from colorama import Fore


class Converter:

    # Change path prefix for .exe
    path_prefix = sys._MEIPASS
    # path_prefix = '.'

    def __init__(self, file, gui):
        self.file = file
        self.gui = gui

        self.gui.update_gui_on_start()
        self.poppler_path = self.path_prefix + '/lib/poppler/bin'
        self.tmp_path = self.path_prefix + '/tmp'
        self.template_path = self.path_prefix + '/template/default.pptx'

        self.file_name_without_ext = self.get_file_name_without_extension()
        self.cpu_threads = self.get_threads()

        pdf_data = self.get_pdf_metadata(file)
        self.pages = pdf_data['Pages']
        self.size = pdf_data['File size']
        self.page_size = pdf_data['Page size']

        self.create_tmp_dir()

        self.convert()
        self.gui.update_gui_on_end()

    def convert(self):
        self.gui.label.pack_forget()
        # self.gui.text_flush()

        # Saving start timestamp
        start = time.time()

        print(f"Конвертуємо файл {self.file}")
        print(Fore.WHITE + "Розмір файлу {:.2f} MB".format(int(self.size.split()[0]) / 10 ** 6))
        print(Fore.WHITE + f"Всього слайдів: {self.pages}")
        print(Fore.YELLOW + "Треба трохи зачекати, триває обробка файлу...")
        print(Fore.YELLOW + "Це може зайняти певний час, не закривайте це вікно...")

        self.gui.label_file.config(text=self.gui.get_file_name(self.file))
        self.gui.label_info.config(text="Розмір файлу {:.2f} MB".format(int(self.size.split()[0]) / 10 ** 6) + f", Всього слайдів: {self.pages}")
        self.gui.label_status.config(text="Триває обробка файлу...", foreground='yellow')

        #     # Convert PDF to images
        images = convert_from_path(
            self.file,
            dpi=300,
            fmt='jpeg',
            poppler_path=self.poppler_path,
            output_folder=self.tmp_path,
            thread_count=self.cpu_threads,
            size=(None, 1440)
        )

        print(Fore.RESET + "____________________________________")

        self.create_pptx_from_images(images)

        # Saving end timestamp
        end = time.time()

        sys.stdout.flush()
        print(Fore.GREEN + f"Конвертування файлу {self.file} завершено!")
        print(Fore.WHITE + f"Витрачено часу: {end - start:.2f}с")

        self.gui.label_status.config(text="Завершено", foreground='green')

        self.gui.label.pack(expand=True)
        return True

    def get_pdf_metadata(self, pdf_file):
        return pdfinfo_from_path(
            pdf_file,
            poppler_path=self.poppler_path
        )

    def get_threads(self):
        if os.cpu_count() > 1:
            cpu_count = os.cpu_count() - 1
        else:
            cpu_count = os.cpu_count()
        return cpu_count

    def get_file_name_without_extension(self):
        return os.path.splitext(self.file)[0]

    def create_tmp_dir(self):
        # creating dir for processed pdf slides
        if not os.path.exists(self.tmp_path):
            os.mkdir(self.tmp_path)

    def create_pptx_from_images(self, images):
        # Create a new PowerPoint presentation
        prs = Presentation(self.template_path)
        height = self.get_height_multiplier()
        prs.slide_width = Inches(16)
        prs.slide_height = Inches(height)

        # Add slides
        for i, image in enumerate(images):
            print(Fore.RED + f"Конвертуємо слайд {i + 1} з {self.pages}")
            self.gui.label_status.config(text="Конвертуємо слайди")
            self.gui.label_progress.config(text=f"{i + 1} / {self.pages}")
            slide = prs.slides.add_slide(prs.slide_layouts[6])
            image_binary = BytesIO()
            image.save(image_binary, 'PNG')
            aspect_ratio = float(image.width) / float(image.height)
            if aspect_ratio > (16/9):
                height = int(Inches(16) / aspect_ratio)
                slide.shapes.add_picture(
                    image_binary,
                    left=0,
                    top=int((Inches(height) - height) / 2),
                    height=height,
                    width=Inches(16)
                )
            else:
                width = int(Inches(height) * aspect_ratio)
                slide.shapes.add_picture(
                    image_binary,
                    left=int((Inches(16) - width) / 2),
                    top=0,
                    height=Inches(height),
                    width=width
                )

        # Save the PowerPoint presentation
        prs.save(self.file_name_without_ext + '.pptx')

    def get_height_multiplier(self):
        matches = re.findall(r'(\d+\.?\d+)', self.page_size)
        width = float(matches[0])
        height = float(matches[1])
        aspect = width / height
        return 16 / aspect
