from PySide6.QtCore import Signal, QUrl
from PySide6.QtGui import QIcon, QAction, QActionGroup, QDesktopServices
from PySide6.QtWidgets import QMenu

from classes.settings import Settings


class MenuUI(QMenu):

    settings_changed = Signal(Settings)

    def __init__(self, app):
        super().__init__()
        self.app = app
        self.settings = Settings()
        self.settings_changed.connect(self.app.worker_thread.update_settings)
        self.version = '0.10'

        # Menu bar
        self.menu_bar = self.app.menuBar()
        self.file_menu = self.menu_bar.addMenu('&Конвертор')
        self.settings_menu = self.menu_bar.addMenu('&Налаштування')
        self.info_menu = self.menu_bar.addMenu('&Інфо')

    def init_menu(self):
        # file - open menu item
        open_action = QAction(QIcon(Settings.get_app_path() + '/assets/file-pdf-regular.svg'), '&Додати файл(и)', self.app)
        open_action.triggered.connect(self.app.open_file)
        open_action.setShortcut('Ctrl+O')
        self.file_menu.addAction(open_action)

        # file - clear menu item
        clear_action = QAction(QIcon(Settings.get_app_path() + '/assets/minus-solid.svg'), '&Очистити список', self.app)
        clear_action.triggered.connect(self.clear_file_list)
        self.file_menu.addAction(clear_action)

        self.file_menu.addSeparator()

        # file - exit menu item
        exit_action = QAction(QIcon(Settings.get_app_path() + '/assets/xmark-solid.svg'), '&Вийти', self.app)
        exit_action.setShortcut('Alt+F4')
        exit_action.triggered.connect(self.app.quit)
        self.file_menu.addAction(exit_action)

        # settings - dpi text menu item
        res_action = QAction('&Роздільна здатність', self.app, disabled=True)
        self.settings_menu.addAction(res_action)

        resolution_group = QActionGroup(self.app)
        # settings - fhd resolution menu item
        fhd_action = QAction('&Full HD (1080px)', self.app, checkable=True, checked=self.settings.resolution == 1920)
        fhd_action.setActionGroup(resolution_group)
        fhd_action.triggered.connect(self.on_resolution_changed)
        self.settings_menu.addAction(fhd_action)

        # settings - qhd resolution menu item
        qhd_action = QAction('&Quad HD (1440px)', self.app, checkable=True, checked=self.settings.resolution == 2560)
        qhd_action.setActionGroup(resolution_group)
        qhd_action.triggered.connect(self.on_resolution_changed)
        self.settings_menu.addAction(qhd_action)

        # settings - uhd resolution menu item
        uhd_action = QAction('&Ultra HD (2160px)', self.app, checkable=True, checked=self.settings.resolution == 3840)
        uhd_action.setActionGroup(resolution_group)
        uhd_action.triggered.connect(self.on_resolution_changed)
        self.settings_menu.addAction(uhd_action)

        # settings - original resolution menu item
        original_action = QAction('&Оригінальний розмір', self.app, checkable=True, checked=self.settings.resolution is None)
        original_action.setActionGroup(resolution_group)
        original_action.triggered.connect(self.on_resolution_changed)
        self.settings_menu.addAction(original_action)

        self.settings_menu.addSeparator()

        # settings - aspect text menu item
        aspect_action = QAction('&Співвідношення сторін', self.app, disabled=True)
        self.settings_menu.addAction(aspect_action)

        aspect_group = QActionGroup(self.app)
        # settings - auto aspect menu item
        aspect_action_auto = QAction('&Автоматично', self.app, checkable=True, checked=self.settings.aspect == 'auto')
        aspect_action_auto.setActionGroup(aspect_group)
        aspect_action_auto.triggered.connect(self.on_aspect_changed)
        self.settings_menu.addAction(aspect_action_auto)

        # settings - 16x9 aspect menu item
        aspect_action_16 = QAction('&16:9', self.app, checkable=True, checked=self.settings.aspect == '16x9')
        aspect_action_16.setActionGroup(aspect_group)
        aspect_action_16.triggered.connect(self.on_aspect_changed)
        self.settings_menu.addAction(aspect_action_16)

        # settings - 4x3 aspect menu item
        aspect_action_4 = QAction('&4:3', self.app, checkable=True, checked=self.settings.aspect == '4x3')
        aspect_action_4.setActionGroup(aspect_group)
        aspect_action_4.triggered.connect(self.on_aspect_changed)
        self.settings_menu.addAction(aspect_action_4)

        self.settings_menu.addSeparator()

        # settings - output text menu item
        output_action = QAction('&Конвертувати в', self.app, disabled=True)
        self.settings_menu.addAction(output_action)

        output_group = QActionGroup(self.app)
        # settings - pptx output menu item
        output_action_pptx = QAction('&PPTX', self.app, checkable=True, checked=self.settings.output == 'pptx')
        output_action_pptx.setActionGroup(output_group)
        output_action_pptx.triggered.connect(self.on_output_changed)
        self.settings_menu.addAction(output_action_pptx)

        # settings - jpg output menu item
        output_action_jpg = QAction('&JPEG', self.app, checkable=True, checked=self.settings.aspect == 'jpg')
        output_action_jpg.setActionGroup(output_group)
        output_action_jpg.triggered.connect(self.on_output_changed)
        self.settings_menu.addAction(output_action_jpg)

        # info - repo menu item
        repo_action = QAction('&GitHub', self.app)
        repo_action.triggered.connect(self.open_github)
        self.info_menu.addAction(repo_action)

        # info - version menu item
        version_action = QAction('&v'+self.version, self.app, disabled=True)
        self.info_menu.addAction(version_action)

        self.file_menu.addSeparator()
        return True

    def on_resolution_changed(self):
        action = self.sender()
        if action.isChecked():
            self.settings.change_resolution(action.text())
            self.settings_changed.emit(self.settings)
        return True

    def on_aspect_changed(self):
        action = self.sender()
        if action.isChecked():
            self.settings.change_aspect(action.text())
            self.settings_changed.emit(self.settings)
        return True

    def on_output_changed(self):
        action = self.sender()
        if action.isChecked():
            self.settings.change_output(action.text())
            self.settings_changed.emit(self.settings)
        return True

    def clear_file_list(self):
        for i in self.app.frames:
            if self.app.frames[i].file.status in [3, 4, 5]:
                self.app.frames[i].frame.hide()
        return True

    @staticmethod
    def open_github():
        QDesktopServices.openUrl(QUrl("https://github.com/viiper94/pdf_to_pptx"))
        return True
