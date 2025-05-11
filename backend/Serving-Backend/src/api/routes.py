from flask import request, jsonify
from ..services.document_processor import DocumentProcessor
from ..services.data_extraction_medical_care import Document_Extractor_Medical_care
from ..services.data_extraction_prescription import Document_Extractor_Prescription
import os

def init_routes(app):
    processor = DocumentProcessor()
    extractor_medical_care = Document_Extractor_Medical_care()
    extractor_prescription = Document_Extractor_Prescription()

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

    @app.route("/extracted-medical-care-data", methods=['POST'])
    def extract_data():
        if 'image' not in request.files:
            return jsonify({"error": "No image provided"}), 400
        file = request.files['image']
        temp_path = "temp_image.jpg"
        try:
            file.save(temp_path)
            result = extractor_medical_care.process_image(temp_path)
            return jsonify(result)
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    @app.route("/extracted-prescription-Data", methods=['POST'])
    def extract_prescription_data():
        if 'image' not in request.files:
            return jsonify({"error": " No image provided"}), 400
        file = request.files['image']
        temp_path = "temp_image.jpg"
        try:
            file.save(temp_path)
            result = extractor_prescription.process_prescription(temp_path)
            return jsonify(result)
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)