from tensorflow.keras.models import load_model
from ..utils.classification import classify_document
import os

class DocumentProcessor:
    def __init__(self, model_path):
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file not found at: {model_path}")
        self.classifier = load_model(model_path)

    def process_image(self, image_path):
        doc_type = classify_document(image_path, self.classifier)
        return {"type": doc_type}