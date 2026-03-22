import os
import fitz
import pytesseract
from PIL import Image
from pdf2image import convert_from_path
import logging

from config.logging_config import setup_logging

logger = logging.getLogger(__name__)

def ocr_image(image_path):

    try:
        img = Image.open(image_path)
        text = pytesseract.image_to_string(img)
        return text

    except Exception as e:
        logger.exception("[DOC] OCR failed for image %s: %s", image_path, e)
        return ""



def clean_text(text):

    lines = text.split("\n")

    cleaned = []

    for line in lines:
        line = line.strip()
        if line:
            cleaned.append(line)

    return "\n".join(cleaned)

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

    setup_logging()

    extension = os.path.splitext(file_path)[1].lower()

    text = ""
    logger.info("[DOC] Processing document: %s", file_path)
    if extension == ".pdf":

        text = extract_text_from_pdf(file_path)

        if len(text.strip()) < 50:
            logger.info("[DOC] PDF appears scanned, running OCR")
            
            logger.info("[DOC] OCR triggered for scanned PDF")
            text = ocr_pdf(file_path)

    elif extension in [".png", ".jpg", ".jpeg"]:

        text = ocr_image(file_path)
    else:
        logger.warning("[DOC] Unsupported extension skipped: %s", extension)

    text = clean_text(text)
    return text

if __name__ == "__main__":

    folder = "bills"

    for root, dirs, files in os.walk(folder):

        for file in files:

            path = os.path.join(root, file)

            print("\nProcessing:", file)

            text = read_document(path)

            print(text[:500])