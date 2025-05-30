from werkzeug.datastructures import FileStorage
from src.config import FILENAME_CLASSIFICATION_RULES

def classify_by_filename(filename: str) -> str | None:
    """
    Classifies the file based on keywords in its filename.
    More robust than simple hardcoding.
    """
    filename_lower = filename.lower()
    for rule in FILENAME_CLASSIFICATION_RULES:
        if any(keyword in filename_lower for keyword in rule["keywords"]):
            return rule["category"]
    return None

def extract_text_from_file(file: FileStorage) -> str | None:
    """
    Placeholder for text extraction logic.
    This would involve:
    1. Detecting file type (e.g., PDF, PNG, JPG, DOCX).
    2. Using appropriate libraries to extract text (e.g., PyPDF2 for PDF, Tesseract for images).
    """
    #TODO 
    return None # Replace with actual extracted text

def classify_file(file: FileStorage):
    """
    Classifies the file using a multi-step approach:
    1. Filename-based classification (as an initial hint or fallback).
    2. Content-based classification (to be implemented).
    """
    # Step 1: Attempt classification by filename
    category_from_filename = classify_by_filename(file.filename)
    if category_from_filename:
        return category_from_filename

    # Step 2: Content-based classification
    extracted_text = extract_text_from_file(file)
    if extracted_text:
        #TODO
        pass
    
    return "unknown file"
