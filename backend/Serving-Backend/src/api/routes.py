from flask import request, jsonify
from ..services.document_processor import DocumentProcessor
from ..services.data_extraction_medical_care import Document_Extractor_Medical_care
import os

def init_routes(app):
    processor = DocumentProcessor()
    extractor_medical_care = Document_Extractor_Medical_care()

    @app.route('/process_document', methods=['POST'])
    def process_document():
        if 'image' not in request.files:
            return jsonify({"error": "No image provided"}), 400
        file = request.files['image']
        temp_path = "temp_image.jpg"
        try:
            file.save(temp_path)
            result = processor.process_image(temp_path)
            return jsonify(result)
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    @app.route('/health', methods=['GET'])
    def health_check():
        return jsonify({"status": "healthy"}), 200

    @app.route("/extracted-ata", methods=['GET'])
    def extract_data():
        if 'image' not in request.files:
            return jsonify({"error": "No image prvided"}), 400
        file = request.files['image']
        temp_path = "temp_image,jpg"
        try:
            file.save(temp_path)
            result = extractor_medical_care.process_image(temp_path)
            return jsonify(result)
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)
