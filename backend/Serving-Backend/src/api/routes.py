import uuid

from flask import request, jsonify
from ..services.document_processor import DocumentProcessor
import os

def init_routes(app):
    processor = DocumentProcessor()

    @app.route('/process_document', methods=['POST'])
    def process_document():
        if 'images' not in request.files:
            return jsonify({"error": "No images provided"}), 400

        files = request.files.getlist('images')
        results = []
        temp_paths = []

        try:
            for file in files:
                if file.filename == '':
                    continue

                temp_path = f"temp_image_{uuid.uuid4()}.jpg"
                temp_paths.append(temp_path)


                file.save(temp_path)
                result = processor.process_image(temp_path)
                results.append(result)

            return jsonify({"results": results})

        except Exception as e:
            return jsonify({"error": str(e)}), 500

        finally:
            for temp_path in temp_paths:
                if os.path.exists(temp_path):
                    os.remove(temp_path)

    @app.route('/health', methods=['GET'])
    def health_check():
        return jsonify({"status": "healthy"}), 200