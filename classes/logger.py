from PySide6.QtWidgets import QMainWindow, QPlainTextEdit
from classes.i18n import i18n


class LoggerWindow(QMainWindow):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.resize(450, 400)
        self.setWindowTitle(i18n.t("Logs"))

        self.text_edit = QPlainTextEdit()
        self.text_edit.setReadOnly(True)

        self.setCentralWidget(self.text_edit)

    def log(self, message: str):
        self.text_edit.appendPlainText(f"> {message}")
