#from .model_loader import load_model_from_db
from ..utils.classification import classify_document
from tensorflow.keras.models import load_model
#from ..utils.ocr import process_ocr
import os

class DocumentProcessor:
    def __init__(self):
        model_path = os.path.join(os.path.dirname(__file__), '..', 'models', 'CNN_model.h5')
        self.classifier = load_model(model_path)

    def process_image(self, image_path):
        doc_type = classify_document(image_path, self.classifier)
        return {"type": doc_type}