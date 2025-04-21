from flask import request, jsonify
from ..services.document_processor import DocumentProcessor

processor = DocumentProcessor()

def init_routes(app):
    @app.route('/process_document', methods=['POST'])
    def process_document():
        if 'image' not in request.files:
            return jsonify({"error": "No image provided"}), 400
        file = request.files['image']
        temp_path = "temp_image.jpg"
        file.save(temp_path)
        result = processor.process_image(temp_path)
        return jsonify(result)

    @app.route('/health', methods=['GET'])
    def health_check():
        return jsonify({"status": "healthy"}), 200