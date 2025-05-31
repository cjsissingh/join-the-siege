"""
This module provides functions for classifying text or files using the Gemini API.
"""
import tempfile
import os
import logging
from werkzeug.datastructures import FileStorage
from google import genai

from src.config import  GEMINI_API_KEY, GEMINI_MODEL, POSSIBLE_CATEGORIES, LOG_LEVEL

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=LOG_LEVEL,
)

client = genai.Client(api_key=GEMINI_API_KEY)

def _clean_and_validate_prediction(prediction_text: str) -> str:
    """
    Cleans the Gemini prediction text and validates it against possible categories.

    Args:
        prediction_text: The raw prediction text from Gemini.

    Returns:
        A valid category string or "unknown file".
    """
    cleaned_prediction = prediction_text.strip().lower().replace("'", "")
    if cleaned_prediction in POSSIBLE_CATEGORIES:
        return cleaned_prediction
    
    logger.warning(
        "Gemini returned an unrecognized category: '%s'. Falling back to 'unknown file'.",
        cleaned_prediction
    )
    return "unknown file"


def classify_text_with_gemini(text: str) -> str | None:
    """
    Classifies the given text into one of the possible categories using the Gemini API.

    Args:
        text: The text content to classify.

    Returns:
        The predicted category string if successful and valid, otherwise None.
    """
    if not GEMINI_API_KEY:
        logger.error("GEMINI_API_KEY is not configured. Cannot use Gemini for classification.")
        return None
    if not text:
        logger.warning("No text provided to classify_text_with_gemini.")
        return None

    try:
        # Ensure categories are clearly listed for the model
        categories_list_str = ", ".join(f"'{cat}'" for cat in POSSIBLE_CATEGORIES)
        prompt = (
            f"Please classify the following document text into one of these categories: {categories_list_str}.\n"
            f"Respond with only the category name. If none of the categories fit well, respond with 'unknown file'.\n\n"
            # Limit text length if necessary - current limit is 4000 characters for safety.
            f"Document Text:\n\"\"\"\n{text[:4000]}\n\"\"\"" 
        )

        response = client.models.generate_content(
            model=f"models/{GEMINI_MODEL}",  # Use fully qualified model name
            contents=prompt
        )
        
        return _clean_and_validate_prediction(response.text)

    except Exception as e:
        logger.error("Error during Gemini API call: %s", e, exc_info=True)
        return None

def classify_file_with_gemini(file: FileStorage) -> str | None:
    """
    Attach the file to the Gemini model and return the predicted category
    """
    if not GEMINI_API_KEY:
        logger.error("GEMINI_API_KEY is not configured. Cannot use Gemini for file classification.")
        return None

    if not file:
        logger.warning("No file provided to classify_file_with_gemini.")
        return None

    try:
        # Create a temporary file to store the FileStorage content
        # The Gemini API's upload_file method expects a file path.
        file_suffix = os.path.splitext(file.filename or "")[1]
        with tempfile.NamedTemporaryFile(delete=True, suffix=file_suffix) as tmp_file:
            file.seek(0)
             # Save FileStorage contents to the temporary file
            file.save(tmp_file.name) 
            # Ensure all data is written to disk
            tmp_file.flush() 

            # Upload the file to Gemini using its path
            logger.debug("Uploading file to Gemini: %s", tmp_file.name)
            
            gemini_file_resource = client.files.upload(
                file=tmp_file.name,  # Pass the path of the temporary file
                config=dict(
                  mime_type=file.mimetype
                )
            )

        # Proceed with classification using the uploaded file resource
        if gemini_file_resource:
            categories_list_str = ", ".join(f"'{cat}'" for cat in POSSIBLE_CATEGORIES)
            prompt = (
                f"Please classify the attached file into one of these categories: {categories_list_str}.\n"
                f"Respond with only the category name. If none of the categories fit well, respond with 'unknown file'.\n\n"
            )
            
            response = client.models.generate_content(
                model=f"models/{GEMINI_MODEL}", # Use fully qualified model name
                contents=[prompt, gemini_file_resource] # Use the file resource from upload_file
            )
            return _clean_and_validate_prediction(response.text)
        else:
            logger.error("Failed to upload file %s to Gemini.", file.filename)
            return None

    except Exception as e:
        logger.error("Error during Gemini API call: %s", e, exc_info=True)
        return None
    
