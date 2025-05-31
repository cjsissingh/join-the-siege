# Heron Coding Challenge - File Classifier

## TL;DR 
- Using a 3 step process:
    1. Infer from the filename
    2. Extract content and classify using Gemini API
    3. Send the whole file to Gemini API

- Deployed to Vercel. 
- Test it: `curl -X POST -F 'file=@files/invoice_1.pdf' https://join-the-siege.vercel.app/classify_file`

## My Solution Overview

To address the challenge of enhancing the initial file classifier, I've implemented a multi-layered solution that significantly improves its capabilities, particularly for handling poorly named files, adapting to new document types, and providing a more robust foundation for scaling.

The core of the solution involves:

1.  **Intelligent Content-Based Classification**:
    *   Leveraging the Google Gemini Large Language Model (LLM) to understand and categorize files based on their actual content, not just filenames.
    *   This is achieved through two main strategies:
        *   Extracting text from various file types (PDFs, images via OCR, DOCX, XLSX, plain text) and sending this text to Gemini.
        *   Uploading the entire file directly to Gemini, allowing it to use its multi-modal capabilities for a more holistic analysis.

2.  **Modular and Extensible Design**:
    *   The codebase is broken down into distinct modules (`app.py` for the API, `classifier.py` for logic, `extractor.py` for text extraction, `gemini.py` for LLM interaction, and `config.py` for settings). This structure enhances maintainability and makes future extensions simpler.

3.  **Configurable and Layered Classification Strategy**:
    *   The system first attempts a quick classification based on filename keywords (defined in `config.py`).
    *   If that's inconclusive, it proceeds to content-based classification using Gemini with extracted text.
    *   As a final step, or for complex files, it can classify by uploading the entire file to Gemini.
    *   A fallback to "unknown file" ensures graceful handling of unclassifiable documents.

## How the Solution Addresses the Challenge

This approach directly tackles the key requirements outlined:

*   **Handling Poorly Named Files**: By prioritizing content analysis via Gemini, the classifier is no longer solely reliant on filenames. It can accurately categorize documents even if their names are uninformative or misleading.

*   **Scaling to New Industries**:
    *   The use of a powerful, general-purpose LLM like Gemini provides inherent flexibility, as these models possess broad knowledge.
    *   New document categories can be introduced by updating the `FILENAME_CLASSIFICATION_RULES` and `POSSIBLE_CATEGORIES` in `config.py`, which then guide the LLM's classification prompts.

*   **Processing Larger Volumes & Diverse File Types**:
    *   The `extractor.py` module supports a wider range of file formats (PDF, PNG, JPG, DOCX, XLSX, TXT).
    *   Initial safeguards like file size limits (`MAX_CONTENT_LENGTH`) and text truncation for the text-based Gemini calls are in place.
    *   Gemini's direct file upload capability is better suited for larger or more complex files where full context is beneficial.
    *   While the current Flask app is synchronous, the modular design and LLM integration provide a strong base for future scaling with asynchronous task queues and other production-grade infrastructure for very high volumes.

*   **Production Readiness**:
    *   **Robustness**: Implemented error handling, logging, input validation (file type, size), and API key checks.
    *   **Maintainability**: Centralized configuration, and clear separation of concerns make the system easier to understand, maintain, and extend.

In essence, the solution transitions from a basic filename-checker to an intelligent, content-aware classification system with a focus on practical enhancements and a solid foundation for future growth.

## Limitations and Future Enhancements

While the current solution significantly improves upon the initial classifier, there are areas for further development, especially for handling very high volumes and increasing production robustness.

### Current Limitations:

*   **Synchronous Processing**: The Flask API handles requests one at a time per worker, which can be a bottleneck for the target of 100,000+ documents daily.
*   **LLM Text Input**: The fixed character limit (`text[:4000]`) for text-based classification might truncate important information in longer documents.
*   **Basic API Error Handling**: Lacks sophisticated retry mechanisms for transient network or Gemini API issues.
*   **Limited Testing**: The current submission does not include a comprehensive test suite (`pytest` tests are mentioned but not provided), which is crucial for ensuring ongoing reliability.
*   **Static Category Derivation**: `POSSIBLE_CATEGORIES` are tied to `FILENAME_CLASSIFICATION_RULES`, which might limit flexibility if categories without clear filename keywords are needed.
*   **Reliance On Filename Accuracy**: If a file is named incorrectly, it could result in a misclassification. The intention of still using filenames is to reduce the number of requests that are sent to Gemini API, reducing the cost of this solution.


### Potential Future Enhancements:

*   **Asynchronous Architecture**:
    *   Implement a task queue (e.g., SQS, EventBridge) to decouple file processing from API requests, enabling much higher throughput.
*   **Advanced LLM Interaction**:
    *   Employ more sophisticated text chunking or summarization for long documents.
    *   Implement caching for LLM responses on identical inputs to reduce API calls and latency.
*   **Enhanced Robustness**:
    *   Introduce retry logic (e.g., exponential backoff) for external API calls.
    *   Set up Dead Letter Queues for persistently failing tasks if a task queue is implemented.
*   **Comprehensive Testing**:
    *   Develop a full suite of unit and integration tests to ensure code quality and catch regressions.
*   **Observability**:
    *   Integrate structured logging and metrics collection (e.g., Prometheus) for better monitoring in a production environment.
*   **Deployment & CI/CD**:
    *   Containerize the application (e.g., Docker) and establish a CI/CD pipeline for automated testing and deployment.
*   **Dynamic Category Management**:
    *   Allow `POSSIBLE_CATEGORIES` to be managed more flexibly, potentially independently of filename rules.

## Deployment (Vercel)

I have deployed the application to Vercel. It is operational (https://join-the-siege.vercel.app/classify_file), but less efficient than running it locally. Vercel presented challenges primarily due to the Python dependencies that rely on underlying system binaries, such as:

*   **`pytesseract`**: Requires Tesseract OCR to be installed in the execution environment.
*   **`python-magic`**: Relies on `libmagic` library.

Vercel's serverless functions have a specific environment, and ensuring these binaries are correctly packaged and accessible can be complex. The build process on Vercel might not automatically include these system-level dependencies without further configuration (e.g., custom build scripts or by using pre-built layers/containers that include them). The text extraction functions may fail, which results in the application falling back to file-based classification. This will have a cost and API rate-limit implication.

    Note: There is a rudimentatry rate-limit (10 requests per minute) on the API to prevent overwhelming of the Gemini API with my personal API key. I will likely pull this site down once my solution has been reviewed. I would prefer not to have a large bill.

**With More Time, I Would Have:**

*   Explored options for including Tesseract and `libmagic` in the Vercel deployment, such as:
    *   Using a custom Docker container for deployment on Vercel, which would allow full control over the environment and inclusion of all necessary system packages.
    *   Researching if Vercel offers specific buildpacks or layers that could provide these common binaries.
*   Considered replacing binary-dependent libraries with pure Python alternatives or cloud-based API services for tasks like OCR if direct binary inclusion proved too difficult for a quick deployment.

## Running the Application Locally

To run the classifier locally, follow these steps:

1.  **Clone the Repository**:
    ```bash
    git clone <your-repository-url>
    cd <repository-name>
    ```

2.  **Set up a Python Virtual Environment**:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
    *Note: This project uses `pytesseract` for OCR, which requires Tesseract OCR to be installed on your system and available in your PATH. Please see the Tesseract installation guide for your operating system.*
    *Similarly, `python-magic` relies on `libmagic`. On Linux, you might install it via `sudo apt-get install libmagic1`. On macOS, `brew install libmagic`.*


4.  **Set Environment Variables**:
    The most crucial environment variable is your Gemini API Key.
    ```bash
    export GEMINI_API_KEY="YOUR_GEMINI_API_KEY_HERE"
    ```
    You can also optionally set:
    ```bash
    export LOG_LEVEL="DEBUG" # (e.g., DEBUG, INFO, WARNING)
    export GEMINI_MODEL="gemini-1.5-flash" # (or another compatible Gemini model)
    ```

5.  **Run the Flask Application**:
    ```bash
    python src/app.py
    ```
    The application will start, typically on `http://127.0.0.1:5000`.

6.  **Test the Classifier**:
    You can use a tool like `curl` to send a file for classification:
    ```bash
    curl -X POST -F 'file=@/path/to/your/sample_file.pdf' http://127.0.0.1:5000/classify_file
    ```
    Replace `/path/to/your/sample_file.pdf` with an actual file path.

