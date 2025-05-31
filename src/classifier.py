"""
This module provides functions for classifying files based on their content and filename.
"""
import logging
from werkzeug.datastructures import FileStorage

from src.extractor import extract_text_from_file
from src.config import FILENAME_CLASSIFICATION_RULES, LOG_LEVEL
from src.gemini import classify_text_with_gemini, classify_file_with_gemini


logger = logging.getLogger(__name__)
logging.basicConfig(
    level=LOG_LEVEL,
)

def classify_by_filename(file: FileStorage) -> str | None:
    """
    Classifies the file based on keywords in its filename.
    More robust than simple hardcoding.
    """
    filename_lower = file.filename.lower()
    for rule in FILENAME_CLASSIFICATION_RULES:
        if any(keyword in filename_lower for keyword in rule["keywords"]):
            return rule["category"]

    return None

def classify_by_content(file: FileStorage) -> str | None:
    """
    Classify the file based on its content, using Gemini.
    Attempts to extract text from the file, and if successful, classifies the file using Gemini.
    Returns the predicted category name if successful and valid, otherwise None.
    """
    extracted_text = extract_text_from_file(file)
    if extracted_text:
        # Log a snippet
        logger.debug("Extracted text for %s: %s...", file.filename, extracted_text) 

        gemini_classification = classify_text_with_gemini(extracted_text)
        if gemini_classification:
            logger.debug("Gemini classification for %s: %s", file.filename, gemini_classification)
            return gemini_classification

    return None

def classify_by_file(file: FileStorage) -> str | None:
    """
    Classify the file using the Gemini API, uploading the file to the API directly.
    Returns the predicted category name if successful and valid, otherwise None.
    """
    gemini_classification = classify_file_with_gemini(file)
    if gemini_classification:
        logger.debug("Gemini classification for %s: %s", file.filename, gemini_classification)
        return gemini_classification

    return None

def classify_file(file: FileStorage):
    """
    Classifies the file using a multi-step approach:
    1. Filename-based classification (as an initial hint or fallback).
    2. Content-based classification using Gemini.
    3. Whole file classification using Gemini.
    Returns the predicted category name.
    """
    # Step 1: Attempt classification by filename
    category_from_filename = classify_by_filename(file)
    if category_from_filename:
        return category_from_filename

    logger.debug("No filename-based classification for %s", file.filename)
   
    # Step 2: Content-based classification
    category_from_content = classify_by_content(file)
    if category_from_content:
        return category_from_content

    logger.debug("Extracted text empty for %s", file.filename)

    # Step 3: Attempt whole file classification with Gemini
    category_from_file = classify_by_file(file)
    if category_from_file:
        return category_from_file

    return "unknown file"
