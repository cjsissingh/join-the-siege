PORT=5000

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
    # Add more rules as needed for different document types or industries
]
