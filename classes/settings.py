class Settings:

    def __init__(self):
        super().__init__()

        self.resolution = 1080
        self.dpi = 300

    def change_resolution(self, res):
        if res == '&FullHD':
            self.resolution = 1080
        if res == '&2K':
            self.resolution = 1440
        if res == '&4K':
            self.resolution = 2160

    def change_dpi(self, dpi):
        if dpi == '&100 DPI':
            self.dpi = 100
        if dpi == '&200 DPI':
            self.dpi = 200
        if dpi == '&300 DPI':
            self.dpi = 300
