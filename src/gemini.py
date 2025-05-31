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

def classify_text_with_gemini(text: str, possible_categories: list[str]) -> str | None:
    """
    Classifies the given text into one of the possible categories using the Gemini API.

    Args:
        text: The text content to classify.
        possible_categories: A list of valid category names.

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
        categories_string = ", ".join(f"'{cat}'" for cat in possible_categories)
        prompt = (
            f"Please classify the following document text into one of these categories: {categories_string}.\n"
            f"Respond with only the category name. If none of the categories fit well, respond with 'unknown file'.\n\n"
            # Limit text length if necessary - Gemini has a limit of 4000 tokens
            f"Document Text:\n\"\"\"\n{text[:4000]}\n\"\"\"" 
        )

        response = client.models.generate_content(
            model=f"models/{GEMINI_MODEL}",  # Use fully qualified model name
            contents=prompt
        )
        predicted_category = response.text.strip().lower().replace("'", "") # Clean up response

        if predicted_category in possible_categories:
            return predicted_category

        logger.warning("Gemini returned an unrecognized category: '%s'", predicted_category)
        return "unknown file" # Or None, depending on desired fallback

    except Exception as e:
        logger.error("Error during Gemini API call: %s", e, exc_info=True)
        return None

def classify_file_with_gemini(file: FileStorage, possible_categories: list[str]) -> str | None:
    """
    Attach the file to the Gemini model and return the predicted category
    """
    if not file:
        logger.warning("No file provided to classify_file_with_gemini.")
        return None

    try:
        # Create a temporary file to store the FileStorage content
        # The Gemini API's upload_file method expects a file path.
        file_suffix = os.path.splitext(file.filename or "")[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_suffix) as tmp_file:
            file.seek(0)
            file.save(tmp_file.name)  # Save FileStorage contents to the temporary file
            tmp_file.flush() # Ensure all data is written to disk

            # Upload the file to Gemini using its path
            # The client.files.upload method can take a file path or an io.IOBase object.
            # Here, we pass the path of the temporary file.
            logger.debug("Uploading file to Gemini: %s", tmp_file.name)
            gemini_file_resource = client.files.upload(
                file=tmp_file.name,  # Pass the path of the temporary file
                config=dict(
                  mime_type='application/pdf'
                )
            )

        # Proceed with classification using the uploaded file resource
        if gemini_file_resource:
            categories_string = ", ".join(f"'{cat}'" for cat in possible_categories)
            prompt = (
                f"Please classify the attached file into one of these categories: {categories_string}.\n"
                f"Respond with only the category name. If none of the categories fit well, respond with 'unknown file'.\n\n"
            )
            
            response = client.models.generate_content(
                model=f"models/{GEMINI_MODEL}", # Use fully qualified model name
                contents=[prompt, gemini_file_resource] # Use the file resource from upload_file
            )
            predicted_category = response.text.strip().lower().replace("'", "")
            if predicted_category in POSSIBLE_CATEGORIES:
                return predicted_category
            logger.warning("Gemini returned an unrecognized category: '%s'", predicted_category)
            return "unknown file"
        return None # Failed to upload file
    except Exception as e:
        logger.error("Error during Gemini API call: %s", e, exc_info=True)
        return None
    
