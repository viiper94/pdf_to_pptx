import os
import sys
import subprocess


class Settings:

    path_prefix = os.path.dirname(os.path.abspath(__file__))
    poppler_path_win = 'lib/poppler/bin'
    poppler_path_osx = 'lib/poppler-osx/bin'

    tmp_path = 'tmp'
    template_path = 'template/default.pptx'

    resolution = 1920
    dpi = 300
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

    def change_dpi(self, dpi):
        if dpi == '&100 DPI':
            self.dpi = 100
        if dpi == '&200 DPI':
            self.dpi = 200
        if dpi == '&300 DPI':
            self.dpi = 300

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
        if output == '&JPEG':
            self.output = 'jpg'

    @staticmethod
    def get_poppler_path():
        prefix = Settings.path_prefix.replace('classes', '')
        if sys.platform.startswith('darwin'):  # macOS
            poppler_path = Settings.poppler_path_osx
        elif sys.platform.startswith('win'):  # Windows
            poppler_path = Settings.poppler_path_win
        return os.path.join(prefix, poppler_path)

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
