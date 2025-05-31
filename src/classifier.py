"""
This module provides functions for classifying files based on their content and filename.
"""
import logging
from werkzeug.datastructures import FileStorage

from src.extractor import extract_text_from_file
from src.config import FILENAME_CLASSIFICATION_RULES, POSSIBLE_CATEGORIES, LOG_LEVEL
from src.gemini import classify_text_with_gemini, classify_file_with_gemini


logger = logging.getLogger(__name__)
logging.basicConfig(
    level=LOG_LEVEL,
)

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

def classify_file(file: FileStorage):
    """
    Classifies the file using a multi-step approach:
    1. Filename-based classification (as an initial hint or fallback).
    2. Content-based classification using Gemini.
    """
    # Step 1: Attempt classification by filename
    category_from_filename = classify_by_filename(file.filename)
    if category_from_filename:
        return category_from_filename

    logger.debug("No filename-based classification for %s", file.filename)
    # Step 2: Content-based classification
    extracted_text = extract_text_from_file(file)

    if extracted_text:
        # Log a snippet
        logger.debug("Extracted text for %s: %s...", file.filename, extracted_text) 
        
        gemini_classification = classify_text_with_gemini(extracted_text, POSSIBLE_CATEGORIES)
        if gemini_classification:
            logger.debug("Gemini classification for %s: %s", file.filename, gemini_classification)
            return gemini_classification

    logger.debug("Extracted text empty for %s", file.filename)

    # Step 3: Attempt classification with Gemini
    gemini_classification = classify_file_with_gemini(file, POSSIBLE_CATEGORIES)
    if gemini_classification:
        logger.debug("Gemini classification for %s: %s", file.filename, gemini_classification)
        return gemini_classification

    return "unknown file"
