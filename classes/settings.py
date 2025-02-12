import os
import sys


class Settings:

    path_prefix = os.path.dirname(os.path.abspath(__file__))

    tmp_path = 'tmp'
    template_path = 'assets/default.pptx'

    resolution = 1920
    aspect = 'auto'
    output = 'pptx'

    def __init__(self):
        super().__init__()

    def change_resolution(self, res):
        if res == '&Full HD (1080px)':
            self.resolution = 1920
        if res == '&Quad HD (1440px)':
            self.resolution = 2560
        if res == '&Ultra HD (2160px)':
            self.resolution = 3840
        if res == '&Оригінальний розмір':
            self.resolution = None

    def change_aspect(self, aspect):
        if aspect == '&Автоматично':
            self.aspect = 'auto'
        if aspect == '&16:9':
            self.aspect = '16x9'
        if aspect == '&4:3':
            self.aspect = '4x3'

    def change_output(self, output):
        if output == '&PPTX':
            self.output = 'pptx'
        if output == '&PNG':
            self.output = 'png'

    @staticmethod
    def get_template_path():
        prefix = Settings.path_prefix.replace('classes', '')
        return os.path.join(prefix, Settings.template_path)

    @staticmethod
    def get_tmp_folder_path():
        prefix = Settings.path_prefix.replace('classes', '')
        return os.path.join(prefix, Settings.tmp_path)

    @staticmethod
    def get_app_path():
        prefix = Settings.path_prefix.replace('classes', '')
        return prefix
