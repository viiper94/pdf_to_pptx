import tkinter as tk
from tkinter import ttk
from tkinter import filedialog as fd
from tkinterdnd2 import DND_FILES, TkinterDnD
from classes.validator import Validator
from classes.converter import Converter
import threading
import re


class Gui:

    frames = {}
    labels = {}
    progress = {}
    separators = {}

    def __init__(self, argv):
        self.root = TkinterDnD.Tk()
        self.root.title("PDF to PPTX Converter")
        self.root.config(background='#2a2a2a')
        self.root.geometry("600x500")
        self.root.resizable(False, False)

        self.label = ttk.Label(self.root, text="Перетягніть файл(и) сюди", font=('Helvetica', 15), background='#2a2a2a', foreground='#eee')
        self.label.pack(expand=True)

        self.style = ttk.Style()
        self.style.theme_use('alt')
        self.style.configure('TFrame', background='#2a2a2a')
        self.style.configure('Horizontal.TProgressbar', background='green')
        self.style.configure('TSeparator', background='#020202')

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
        if file_paths:
            threading.Thread(target=self.process_files, args=(file_paths,)).start()

    def on_drop(self, event):
        file_paths = event.data
        if file_paths:
            paths_list = self.split_string_with_escapes(file_paths)
            threading.Thread(target=self.process_files, args=(paths_list,)).start()

    def process_files(self, file_path):
        validated_files = Validator.validate(file_path)
        self.update_gui_on_start(validated_files)
        for i, item in enumerate(validated_files):
            Converter(i, item, self)

    def split_string_with_escapes(self, input_string):
        pattern = r'\{[^\}]*\}|[^ ]+'
        matches = re.findall(pattern, input_string)
        result = [match.strip('{}') for match in matches]
        return result

    def update_gui_on_start(self, files):
        self.label.pack_forget()
        for index, file_path in enumerate(files):
            self.frames[index] = ttk.Frame(self.root)
            self.frames[index].pack(fill=tk.X)

            self.frames[index].columnconfigure(0, weight=2)
            self.frames[index].columnconfigure(1, weight=1)

            self.labels[index] = {}
            self.labels[index]['name'] = ttk.Label(self.frames[index], font=('Helvetica', 10), background='#2a2a2a', foreground='#eee')
            self.labels[index]['size'] = ttk.Label(self.frames[index], font=('Helvetica', 8), background='#2a2a2a', foreground='#5d5d5d')
            self.labels[index]['slides'] = ttk.Label(self.frames[index], font=('Helvetica', 8), background='#2a2a2a', foreground='#5d5d5d')
            self.labels[index]['status'] = ttk.Label(self.frames[index], font=('Helvetica', 9), background='#2a2a2a', foreground='#5d5d5d')
            self.progress[index] = ttk.Progressbar(self.frames[index], mode="indeterminate", length=150)
            self.separators[index] = ttk.Separator(self.frames[index])

            self.labels[index]['name'].config(text=self.get_file_name(file_path))
            self.labels[index]['status'].config(text="В черзі")

            self.labels[index]['name'].grid(column=0, row=0, sticky=tk.EW, padx=(10, 0), pady=(10, 0))
            self.labels[index]['size'].grid(column=0, row=1, sticky=tk.EW, padx=(10, 0))
            self.labels[index]['slides'].grid(column=0, row=2, sticky=tk.EW, padx=(10, 0))
            self.labels[index]['status'].grid(column=1, row=2, sticky=tk.E, padx=15)
            self.separators[index].grid(columnspan=2, column=0, row=3, sticky=tk.EW, pady=5)
            self.progress[index].grid(column=1, row=0, sticky=tk.E, rowspan=2, padx=15)
            self.progress[index].start(interval=5)

        self.unbind_events()

    def update_gui_on_file_process(self, index, file_pages, file_size):
        self.labels[index]['size'].config(text="Розмір файлу {:.2f} MB".format(int(file_size.split()[0]) / 10 ** 6))
        self.labels[index]['slides'].config(text=f"Слайдів: {file_pages}")
        self.labels[index]['status'].config(text="Триває обробка файлу...", foreground='yellow')

    def update_gui_on_convertion(self, index, current, total):
        self.labels[index]['status'].config(text=f"Конвертуємо слайди ({current}/{total})", foreground='red')
        self.progress[index].stop()
        self.progress[index].config(mode='determinate')
        self.update_progress(index, current, total)

    def update_gui_on_end(self, index, time_spent):
        self.labels[index]['status'].config(text=f"Завершено ({time_spent:.2f}с)", foreground='green')
        self.progress[index]['value'] = 100

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

    def update_progress(self, index, current, total):
        self.progress[index]['value'] = current/total*100
