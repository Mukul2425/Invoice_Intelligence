import os
import fitz
import pytesseract
from PIL import Image
from pdf2image import convert_from_path

def ocr_image(image_path):

    img = Image.open(image_path)

    text = pytesseract.image_to_string(img)

    return text

def extract_text_from_pdf(pdf_path):

    doc = fitz.open(pdf_path)

    text = ""

    for page in doc:
        text += page.get_text()

    return text

def ocr_pdf(pdf_path):

    images = convert_from_path(pdf_path)

    text = ""

    for img in images:
        text += pytesseract.image_to_string(img)

    return text

def read_document(file_path):

    extension = os.path.splitext(file_path)[1].lower()

    text = ""

    if extension == ".pdf":

        text = extract_text_from_pdf(file_path)

        if len(text.strip()) < 50:
            print("PDF appears scanned, running OCR...")
            text = ocr_pdf(file_path)

    elif extension in [".png", ".jpg", ".jpeg"]:

        text = ocr_image(file_path)

    return text

if __name__ == "__main__":

    folder = "bills"

    for root, dirs, files in os.walk(folder):

        for file in files:

            path = os.path.join(root, file)

            print("\nProcessing:", file)

            text = read_document(path)

            print(text[:500])