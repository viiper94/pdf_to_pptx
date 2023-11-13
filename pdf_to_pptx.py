import sys
from PySide6 import QtWidgets
from classes.qt import QtApp


if __name__ == "__main__":

    app = QtWidgets.QApplication(sys.argv)
    widget = QtApp(sys.argv)

    sys.exit(app.exec())
