import re
import fitz #PyMuPDF

def clean_text(txt):
    text = re.sub(r"[^\x20-\x7D]+", " ", txt)
    text = re.sub(r"(\\x[0-9a-fA-F]{2}){2,4}", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text

def pdf_to_text(pdf_path):
    document = fitz.open(pdf_path)
    text = ""
    for page in document:
        text += page.get_text()

    return clean_text(text)