import os
import re
import time
from io import BytesIO
from pdf2image import convert_from_path
from pptx import Presentation
from pptx.util import Inches

from classes.info_handler import InfoHandler


class Convertor:

    def __init__(self, index, file, password, thread, settings):
        self.thread = thread
        self.file = file
        self.password = password
        self.index = index
        self.settings = settings

        self.file_name_without_ext = self.get_file_name_without_extension()
        self.cpu_threads = self.get_threads()

        pdf_data = InfoHandler.get_pdf_metadata(self.file, self.password)
        self.pages = pdf_data['Pages']
        self.page_size = pdf_data['Page size']

        self.thread.file_process_start.emit(index)

        self.create_tmp_dir()

    def convert(self):
        # Saving start timestamp
        start = time.time()

        try:
            # Convert PDF to images
            images = convert_from_path(
                self.file,
                dpi=self.settings.dpi,
                fmt='png',
                poppler_path=self.settings.get_poppler_path(),
                output_folder=self.settings.get_tmp_folder_path(),
                thread_count=self.cpu_threads,
                use_pdftocairo=True,
                userpw=self.password,
                size=(self.settings.resolution, None)
            )

            if self.settings.output == 'pptx':
                file_path = self.create_pptx_from_images(images)
            else:
                file_path = self.save_images(images)

            # Saving end timestamp
            end = time.time()
            time_spent = end - start

            self.thread.file_process_end.emit(self.index, time_spent, file_path)

        except Exception:
            self.thread.file_process_failed.emit(self.index, "Виникла помилка =(")

        return True

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
        if not os.path.exists(self.settings.get_tmp_folder_path()):
            os.mkdir(self.settings.get_tmp_folder_path())

    def create_pptx_from_images(self, images):
        # Create a new PowerPoint presentation
        prs = Presentation(self.settings.get_template_path())
        page_height = self.get_height_multiplier()
        slide_width = Inches(16)
        slide_height = Inches(page_height)
        slide_aspect = slide_width / slide_height
        prs.slide_width = slide_width
        prs.slide_height = slide_height

        # Add slides
        for i, image in enumerate(images):
            self.thread.file_process_progress.emit(self.index, i + 1, self.pages)
            slide = prs.slides.add_slide(prs.slide_layouts[6])
            image_binary = BytesIO()
            image.save(image_binary, 'PNG')
            aspect_ratio = float(image.width) / float(image.height)
            if aspect_ratio >= slide_aspect:
                height = int(slide_width / aspect_ratio)
                slide.shapes.add_picture(
                    image_binary,
                    left=int(0),
                    top=int((slide_height - height) / 2),
                    height=height,
                    width=slide_width
                )

            else:
                width = int(Inches(page_height) * aspect_ratio)
                slide.shapes.add_picture(
                    image_binary,
                    left=int((slide_width - width) / 2),
                    top=int(0),
                    height=slide_height,
                    width=width
                )

        # Save the PowerPoint presentation
        file_path = self.file_name_without_ext + '.pptx'
        prs.save(file_path)
        return file_path

    def save_images(self, images):
        # creating dir with images
        output_path = ''
        if not os.path.exists(self.file_name_without_ext):
            os.mkdir(self.file_name_without_ext)

        for i, image in enumerate(images, start=1):
            self.thread.file_process_progress.emit(self.index, i, self.pages)
            numbered_filename = f"{i:02d}.jpg"  # Pad with zeros for consistent numbering
            output_path = os.path.join(self.file_name_without_ext, numbered_filename)
            image.save(output_path, 'JPEG')

        return output_path

    def get_height_multiplier(self):
        if self.settings.aspect == 'auto':
            matches = re.findall(r'(\d+\.?\d+)', self.page_size)
            width = float(matches[0])
            height = float(matches[1])
            aspect = width / height
            return 16 / aspect
        if self.settings.aspect == '16x9':
            return 9
        if self.settings.aspect == '4x3':
            return 12
