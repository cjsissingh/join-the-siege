import os

PORT=5000
LOG_LEVEL = 'DEBUG'

# Allowed file extensions for upload
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'doc', 'docx', 'xls', 'xlsx'}

# Maximum file size for upload (e.g., 10MB)
MAX_CONTENT_LENGTH = 10 * 1024 * 1024

# Rules for filename-based classification
# This provides a basic level of classification and can be expanded.
# For more robust classification, content analysis is preferred.
FILENAME_CLASSIFICATION_RULES = [
    {"keywords": ["drivers_licence", "driver licence", "dl", "drivers_license", "driver license"], "category": "drivers_licence"},
    {"keywords": ["bank_statement", "bank statement"], "category": "bank_statement"},
    {"keywords": ["invoice", "inv"], "category": "invoice"},
    {"keywords": ["passport"], "category": "passport"},
    {"keywords": ["utility_bill", "utility bill"], "category": "utility_bill"},
    {"keywords": ["check"], "category": "check"},
    {"keywords": ["credit_card", "credit card"], "category": "credit_card"},
    {"keywords": ["debit_card", "debit card"], "category": "debit_card"},
    {"keywords": ["receipt", "reciept"], "category": "receipt"},
    {"keywords": ["tax_form", "tax form"], "category": "tax_form"},
    {"keywords": ["work_permit", "work permit"], "category": "work_permit"},
]
POSSIBLE_CATEGORIES = list(set(rule["category"] for rule in FILENAME_CLASSIFICATION_RULES))

# Gemini API Key
# It's best practice to load this from an environment variable
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
# Allow experimentation with different Gemini models - easy to switch
GEMINI_MODEL = os.environ.get("GEMINI_MODEL") or "gemini-1.5-flash"

