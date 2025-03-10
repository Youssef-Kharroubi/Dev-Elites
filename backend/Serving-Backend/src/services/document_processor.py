from .model_loader import load_model_from_db
from ..utils.classification import classify_document
from ..utils.ocr import process_ocr

class DocumentProcessor:
    def __init__(self):
        self.classifier = load_model_from_db("classifier","1")

    def process_image(self, image_path):
        doc_type = classify_document(image_path, self.classifier)
        text = process_ocr(None, doc_type)
        return {"type": doc_type, "text": text}