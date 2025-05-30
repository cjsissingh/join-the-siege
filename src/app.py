from flask import Flask, request, jsonify
import logging

from src.classifier import classify_file
from src.config import ALLOWED_EXTENSIONS, MAX_CONTENT_LENGTH, PORT
app = Flask(__name__)

logging.basicConfig(level=logging.INFO)
def is_allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def hello():
    return 'Hello, World!'

@app.route('/classify_file', methods=['POST'])
def classify_file_route():

    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if not is_allowed_file(file.filename):
        return jsonify({"error": f"File type not allowed"}), 400

    if request.content_length > MAX_CONTENT_LENGTH:
        return jsonify({"error": "File too large"}), 413

    try:
        file_class = classify_file(file)
        return jsonify({"file_class": file_class}), 200
    except Exception as e:
        app.logger.error(f"Error classifying file: {e}", exc_info=True)
        return jsonify({"error": "Internal server error during classification"}), 500

if __name__ == '__main__':
    app.run(debug=True, port=PORT)
