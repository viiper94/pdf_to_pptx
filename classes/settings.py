class Settings:

    def __init__(self):
        super().__init__()

        self.resolution = 1080

    def change_resolution(self, res):
        if res == '&FullHD':
            self.resolution = 1080
        if res == '&2K':
            self.resolution = 1440
        if res == '&4K':
            self.resolution = 2160
        print(self.resolution)
