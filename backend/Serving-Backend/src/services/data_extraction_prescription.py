import os
import json
import cv2
import easyocr
from dotenv import load_dotenv
from transformers import TrOCRProcessor, VisionEncoderDecoderModel
from tensorflow.keras.models import load_model
from ..utils.Modeling_OCR.prescription_extraction import predict_text

load_dotenv()

class Document_Extractor_Prescription:
    def __init__(self):
        base_path = os.path.dirname(__file__)
        cnn_model_path = os.path.join(base_path, '..', 'models', 'text_classification_model.h5')
        self.cnn_model = load_model(cnn_model_path)
        self.VisionTROCR = VisionEncoderDecoderModel.from_pretrained("microsoft/trocr-large-handwritten")
        self.TROCR = TrOCRProcessor.from_pretrained("microsoft/trocr-large-handwritten")

    def process_prescription(self, image_path):
        reader = easyocr.Reader(['fr'], gpu=False)
        try:
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError(f"Failed to load image: {image_path}")

            results = predict_text(image_path,self.cnn_model,reader)
            return results
        except Exception as e:
            print(f"Error processing prescription image : {str(e)}")
            return json.dumps({"error": str(e)},ensure_ascii=False, indent=2)