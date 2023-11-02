import os
import time
import tkinter as tk
from tkinter import filedialog as fd
from tkinterdnd2 import DND_FILES, TkinterDnD
from PIL import Image
from classes.validator import Validator
from classes.converter import Converter
import threading
import re


class Gui:

    def __init__(self, argv):
        self.root = TkinterDnD.Tk()
        self.root.title("PDF to PPTX Converter")
        self.root.config(background='#2a2a2a')
        self.root.geometry("600x500")
        self.root.resizable(False, False)

        self.label = tk.Label(self.root, text="Перетягніть файл(и) сюди", font=('Open Sans', 15), background='#2a2a2a', foreground='#eee')
        self.label.pack(expand=True)

        self.label_file = tk.Label(self.root, text="", font=('Open Sans', 12), background='#2a2a2a', foreground='#eee', pady=15)
        self.label_info = tk.Label(self.root, text="", font=('Open Sans', 9), background='#2a2a2a', foreground='#5d5d5d')
        self.label_status = tk.Label(self.root, text="", font=('Open Sans', 10), background='#2a2a2a', foreground='#eee')
        self.label_progress = tk.Label(self.root, text="", font=('Open Sans', 11), pady=10, foreground='red', background='#2a2a2a')

        self.root.drop_target_register(DND_FILES)

        if len(argv) > 1:
            argv.pop(0)
            threading.Thread(target=self.process_files, args=(argv,)).start()
        else:
            self.bind_events()

    def on_click(self, event):
        file_paths = fd.askopenfilenames(
            title='Оберіть PDF файл(и)',
            filetypes=[('PDF файли', '*.pdf')])
        threading.Thread(target=self.process_files, args=(file_paths,)).start()

    def on_drop(self, event):
        file_paths = event.data
        if file_paths:
            paths_list = self.split_string_with_escapes(file_paths)
            threading.Thread(target=self.process_files, args=(paths_list,)).start()

    def process_files(self, file_path):
        validated_files = Validator.validate(file_path)
        Image.MAX_IMAGE_PIXELS = 1000000000
        for item in validated_files:
            Converter(item, self)

    def split_string_with_escapes(self, input_string):
        pattern = r'\{[^\}]*\}|[^ ]+'
        matches = re.findall(pattern, input_string)
        result = [match.strip('{}') for match in matches]
        return result

    def update_gui_on_start(self):
        self.label.pack_forget()
        self.label_file.pack()
        self.label_info.pack()
        self.label_status.pack()
        self.label_progress.pack()
        self.unbind_events()

    def update_gui_on_end(self):
        self.label.pack(expand=True)
        self.bind_events()

    def bind_events(self):
        self.root.bind('<Button-1>', self.on_click)
        self.root.dnd_bind('<<Drop>>', self.on_drop)

    def unbind_events(self):
        self.root.unbind('<Button-1>')
        self.root.unbind('<<Drop>>')

    def get_file_name(self, path):
        parts = path.split('/')
        result = parts[-1]
        return result
