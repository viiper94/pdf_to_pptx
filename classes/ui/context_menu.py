from PySide6.QtGui import QAction
from PySide6.QtWidgets import QMenu

from classes.settings import Settings


class ContextMenu(QMenu):

    def __init__(self, file_frame, theme):
        super().__init__()

        self.file_frame = file_frame
        self.open_action = None
        self.cancel_action = None
        self.theme = theme
        self.load_stylesheet()
        self.add_cancel_option()

    def load_stylesheet(self):
        path = f"{Settings.get_app_path()}/assets/styles/context-{self.theme}.qss"
        try:
            with open(path, 'r') as file:
                self.setStyleSheet(file.read())
        except FileNotFoundError:
            print(f"Warning: Stylesheet not found at {path}")

    def show_menu(self, position):
        self.exec(self.file_frame.frame.mapToGlobal(position))

    def cancel_conversion(self):
        self.file_frame.app.cancel_conversion(self.file_frame.index)

    def add_cancel_option(self):
        text = f'Скасувати конвертацію файлу'

        self.cancel_action = QAction(text, self.file_frame.frame)
        self.cancel_action.triggered.connect(self.file_frame.cancel_conversion)
        self.addAction(self.cancel_action)

    def add_open_option(self):
        text = f'Показати файл в папці'

        self.open_action = QAction(text, self.file_frame.frame)
        self.open_action.triggered.connect(self.file_frame.on_file_open_click)
        self.addAction(self.open_action)
        pass

    def remove_cancel_option(self):
        self.removeAction(self.cancel_action)

    def remove_open_option(self):
        self.removeAction(self.open_action)
