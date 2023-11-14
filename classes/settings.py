import sys
import os


class Settings:

    # Change path prefix for .exe
    # path_prefix = sys._MEIPASS        # path for Windows
    path_prefix = os.path.dirname(os.path.abspath(__file__))        # path for Mac OS
    # path_prefix = '.'                 # path for development

    poppler_path = 'lib/poppler-osx/bin'
    tmp_path = 'tmp'
    template_path = 'template/default.pptx'

    resolution = 1080
    dpi = 300

    def __init__(self):
        super().__init__()

    def change_resolution(self, res):
        if res == '&Full HD (1080px)':
            self.resolution = 1080
        if res == '&Quad HD (1440px)':
            self.resolution = 1440
        if res == '&Ultra HD (2160px)':
            self.resolution = 2160

    def change_dpi(self, dpi):
        if dpi == '&100 DPI':
            self.dpi = 100
        if dpi == '&200 DPI':
            self.dpi = 200
        if dpi == '&300 DPI':
            self.dpi = 300

    @staticmethod
    def get_poppler_path():
        prefix = Settings.path_prefix.replace('/classes', '')
        return os.path.join(prefix, Settings.poppler_path)

    @staticmethod
    def get_template_path():
        prefix = Settings.path_prefix.replace('/classes', '')
        return os.path.join(prefix, Settings.template_path)

    @staticmethod
    def get_tmp_folder_path():
        prefix = Settings.path_prefix.replace('/classes', '')
        return os.path.join(prefix, Settings.tmp_path)

