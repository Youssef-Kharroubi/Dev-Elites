import cv2
import easyocr
import numpy as np
import pandas as pd
import json
import logging
import os
from dotenv import load_dotenv
from ultralytics import YOLO
from PIL import Image
from ..services.document_processor import DocumentProcessor
from ..utils.Modeling_OCR.medical_care_form_extraction import process_detections, detect_all_words, extract_texts_from_images
from transformers import TrOCRProcessor, VisionEncoderDecoderModel
from tensorflow.keras.models import load_model

load_dotenv()
CLASS_NAMES = json.loads(os.getenv("CLASS_NAMES"))
Processor = DocumentProcessor()
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)
class Document_Extractor_Medical_care:
    def __init__(self):
        base_path = os.path.dirname(__file__)
        yolo_model_path = os.path.join(base_path, '..', 'models', 'best.pt')  # YOLO model
        insurance_model_path = os.path.join(base_path, '..', 'models', 'insurance_classifier_vgg16.h5')
        self.yolo_model = YOLO(yolo_model_path)
        self.insurance_model = load_model(insurance_model_path)
        self.vision_encoder = VisionEncoderDecoderModel.from_pretrained("microsoft/trocr-large-handwritten")

    def process_image(self, image_path):
        try:
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError(f"Failed to load image: {image_path}")

            results = self.yolo_model(image, imgsz=640, device=None)

            predicted_company = Processor.process_image_internal(image_path)
           # if predicted_company not in ["STAR", "BH", "CNAM"]:
            #    raise ValueError(f"Invalid predicted company: {predicted_company}")

            cropped_regions = process_detections(image, results, CLASS_NAMES)

            cropped_text_regions = []
            for label, cropped_image in cropped_regions:
                detected_words = detect_all_words(cropped_image, lang='fr', predicted_company=predicted_company)
                if detected_words:
                    for idx, word_image in enumerate(detected_words, start=1):
                        cropped_text_regions.append((label, word_image))

            extracted_data = extract_texts_from_images(cropped_text_regions)

            return extracted_data

        except Exception as e:
            print(f"Error processing image: {str(e)}")
            return json.dumps({"error": str(e)}, ensure_ascii=False, indent=2)
