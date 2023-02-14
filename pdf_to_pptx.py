import sys
import os
import collections.abc
from pptx import Presentation
from pptx.util import Inches
from pdf2image import convert_from_path
from io import BytesIO

def pdf_to_pptx(pdf_file):
    # Get the file name without the extension
    file_name = os.path.splitext(pdf_file)[0]
    
    print(f"Конвертуємо файл {pdf_file}...")
    print("Треба трохи зачекати, йде обробка файлу...")
    print("Це може зайняти певний час, не закривайте це вікно...")
    
    # Convert PDF to images
    images = convert_from_path(pdf_file, 300, poppler_path=sys._MEIPASS+'/poppler')
    
    num_slides = len(images)

    print(f"Всього слайдів: {num_slides}")
    print("____________________________________")

    # Create a new PowerPoint presentation
    prs = Presentation(sys._MEIPASS+"/template/default.pptx")
    prs.slide_width = Inches(16)
    prs.slide_height = Inches(9)

    # Add slides
    for i, image in enumerate(images):
        print(f"Конвертуємо слайд {i+1} з {num_slides}")
        slide = prs.slides.add_slide(prs.slide_layouts[0])
        image_binary = BytesIO()
        image.save(image_binary, 'PNG')
        aspect_ratio = float(image.width) / float(image.height)
        if aspect_ratio > (16/9):
            height = int(Inches(16) / aspect_ratio)
            picture = slide.shapes.add_picture(image_binary, 0, int((Inches(9) - height) / 2), height=height, width=Inches(16))
        else:
            width = int(Inches(9) * aspect_ratio)
            picture = slide.shapes.add_picture(image_binary, int((Inches(16) - width) / 2), 0, height=Inches(9), width=width)

    # Save the PowerPoint presentation
    prs.save(file_name + '.pptx')

    print("Конвертування завершено!")
    
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: pdf_to_pptx.exe <pdf_file>")
    else:
        pdf_to_pptx(sys.argv[1])
