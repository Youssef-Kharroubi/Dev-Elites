import cv2
import easyocr
import numpy as np
import json
import re
import pandas as pd
from ultralytics import YOLO
from PIL import Image
from transformers import TrOCRProcessor, VisionEncoderDecoderModel
from tensorflow.keras.models import load_model




def process_detections(image, results, class_names):
    crop_counter = 1
    cropped_regions = []
    for result in results:
        boxes = result.boxes.xyxy  
        confidences = result.boxes.conf
        class_ids = result.boxes.cls

        for box, conf, cls_id in zip(boxes, confidences, class_ids):
            x1, y1, x2, y2 = map(int, box)
            class_id = int(cls_id)
            label = class_names[class_id]
            confidence = float(conf)
            print(f"Confidence is: {confidence:.2f}")
            if label not in ["designation", "date", "honoraire"]:
                if x2 > x1 and y2 > y1:
                    cropped_image = image[y1:y2, x1:x2]
                    cropped_regions.append((label, cropped_image))
                    crop_counter += 1
    return cropped_regions

def horizontal_proximity(box1, box2, proximity_thresh=40, alignment_thresh=15):
    x1_min, y1_min, x1_max, y1_max = box1
    x2_min, y2_min, x2_max, y2_max = box2

    if abs(x1_min - x2_max) < proximity_thresh or abs(x2_min - x1_max) < proximity_thresh:
        y_center_1 = (y1_min + y1_max) / 2
        y_center_2 = (y2_min + y2_max) / 2
        if abs(y_center_1 - y_center_2) < alignment_thresh:
            return True
    return False


def merge_boxes(boxes):
    merged = []
    used = [False] * len(boxes)

    for i in range(len(boxes)):
        if used[i]:
            continue
        x1, y1, x2, y2 = boxes[i]
        new_box = [x1, y1, x2, y2]
        used[i] = True
        for j in range(i + 1, len(boxes)):
            if not used[j] and horizontal_proximity(new_box, boxes[j]):
                bx1, by1, bx2, by2 = boxes[j]
                new_box = [
                    min(new_box[0], bx1),
                    min(new_box[1], by1),
                    max(new_box[2], bx2),
                    max(new_box[3], by2)
                ]
                used[j] = True
        merged.append(new_box)
    return merged

def detect_all_words(image, lang, proximity_threshold=40, predicted_company="BH"):
    reader = easyocr.Reader([lang], gpu=False)
    results = reader.readtext(image, detail=1, paragraph=False, min_size=10, text_threshold=0.3)

    if len(results) == 0:
        print("No text detected.")
        return []

    raw_boxes = []
    for (bbox, text, prob) in results:
        (tl, tr, br, bl) = bbox
        x_min = int(min([pt[0] for pt in bbox]))
        y_min = int(min([pt[1] for pt in bbox]))
        x_max = int(max([pt[0] for pt in bbox]))
        y_max = int(max([pt[1] for pt in bbox]))
        raw_boxes.append([x_min, y_min, x_max, y_max])

    merged_boxes = merge_boxes(raw_boxes)
    
    cropped_regions = []
    for idx, (x1, y1, x2, y2) in enumerate(merged_boxes):
        if predicted_company in ["BH", "CNAM"]:
            if y2 > y1 and x2 > x1:
                cropped = image[y1:y2, x1:x2]
                cropped_regions.append(cropped)
        else:
            if (y2 - y1) > 40 and (x2 - x1) > 40:
                cropped = image[y1:y2, x1:x2]
                cropped_regions.append(cropped)
    return cropped_regions

def format_unquoted_json(data):
    """Format a dictionary as a JSON-like string with unquoted keys."""
    def quote_value(value):
        return f'"{value}"' if isinstance(value, str) else str(value)

    items = [f"{key}: {quote_value(value)}" for key, value in data.items()]
    return "{\n  " + ",\n  ".join(items) + "\n}"

def extract_texts_from_images(cropped_regions):
    processor = TrOCRProcessor.from_pretrained("microsoft/trocr-large-handwritten")
    model = VisionEncoderDecoderModel.from_pretrained("microsoft/trocr-large-handwritten")

    extracted_data = {
        "adherent_name": [],
        "matricule_cnam": [],
        "matricule_adherent": [],
        "adresse_adherent": [],
        "cin_ou_passeport": [],
        "malade_name": [],
        "date_naissance": [],
        "id_field": []
    }

    for label, cropped_image in cropped_regions:
        try:
            image = Image.fromarray(cv2.cvtColor(cropped_image, cv2.COLOR_BGR2RGB))
            pixel_values = processor(images=image, return_tensors="pt").pixel_values
            generated_ids = model.generate(pixel_values)
            predicted_text = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]

            if "nom et prenom de adherent" in label:
                extracted_data["adherent_name"].append(predicted_text)
            elif "matricule cnam" in label:
                predicted_text = re.sub(r'[^0-9]', '', predicted_text)
                extracted_data["matricule_cnam"].append(predicted_text)
            elif "matricule de adherent" in label:
                predicted_text = re.sub(r'[^0-9]', '', predicted_text)
                extracted_data["matricule_adherent"].append(predicted_text)
            elif "addresse de ladherent" in label:
                extracted_data["adresse_adherent"].append(predicted_text)
            elif "numero cin ou passeport" in label:
                predicted_text = re.sub(r'[^0-9]', '', predicted_text)
                extracted_data["cin_ou_passeport"].append(predicted_text)
            elif "nom et prenom du malade" in label:
                extracted_data["malade_name"].append(predicted_text)
            elif "date de naissance" in label:
                predicted_text = re.sub(r'[^0-9/]', '', predicted_text)
                extracted_data["date_naissance"].append(predicted_text)
            elif label.startswith("id") or "id_" in label:
                predicted_text = re.sub(r'[^0-9]', '', predicted_text)
                extracted_data["id_field"].append(predicted_text)

            print(f"Extracted text from {label}: {predicted_text}")

        except Exception as e:
            print(f"Error processing {label}: {str(e)}")

    # Normalize the extracted data to single strings
    normalized_data = {
        "id_field": extracted_data["id_field"][0] if extracted_data["id_field"] else "",
        "adherent_name": " ".join(filter(None, extracted_data["adherent_name"])),
        "matricule_cnam": extracted_data["matricule_cnam"][0] if extracted_data["matricule_cnam"] else "",
        "matricule_adherent": extracted_data["matricule_adherent"][0] if extracted_data["matricule_adherent"] else "",
        "cin_ou_passeport": extracted_data["cin_ou_passeport"][0] if extracted_data["cin_ou_passeport"] else "",
        "adresse_adherent": ", ".join(filter(None, extracted_data["adresse_adherent"])),
        "malade_name": " ".join(filter(None, extracted_data["malade_name"])),
        "date_naissance": extracted_data["date_naissance"][0] if extracted_data["date_naissance"] else ""
    }

    return format_unquoted_json(normalized_data)

#call of the code
# extract_texts_from_images(cropped_text_regions)

