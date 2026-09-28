from PySide6.QtCore import QObject, Signal
import json
from pathlib import Path


class I18n(QObject):

    language_changed = Signal()

    def __init__(self, lang="en", i18n_dir="i18n"):
        super().__init__()
        self.i18n_dir = Path(i18n_dir)
        self.strings = {}
        self.lang = lang
        self._load(lang)

    def _load(self, lang):
        path = self.i18n_dir / f"{lang}.json"
        self.strings = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}

    def set_language(self, lang):
        self.lang = lang
        self._load(lang)
        self.language_changed.emit()

    def t(self, text, **kwargs):
        translated = self.strings.get(text, text)
        return translated.format(**kwargs) if kwargs else translated

i18n = I18n(lang="en")
